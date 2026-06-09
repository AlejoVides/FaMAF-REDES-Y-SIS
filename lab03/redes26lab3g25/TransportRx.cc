#ifndef TRANSPORTRX
#define TRANSPORTRX

#include <string.h>
#include <omnetpp.h>
#include "TransportPkt_m.h"
#include "PacketKind.h"

using namespace omnetpp;

class TransportRx : public cSimpleModule {
private:
    cMessage *endServiceEvent;      // evento interno para despachar paquetes al sink
    cQueue rxBuffer;                // buffer de recepción
    int bufferSize;                 // capacidad máxima del buffer
    int rwnd;                       // ventana de recepción (espacio libre)
    long droppedPackets;            // contador de paquetes descartados
    cOutVector bufferSizeVector;    // ocupación del buffer en el tiempo
    cOutVector packetDropVector;    // paquetes descartados en el tiempo
    cQueue ackQueue;                // cola para almacenar ACKs pendientes de envío
    cMessage *sendFeedbackEvent;    // evento interno para despachar ACKs al transmisor
public:
    TransportRx();
    virtual ~TransportRx();
protected:
    virtual void initialize();
    virtual void finish();
    virtual void handleMessage(cMessage *msg);
};

Define_Module(TransportRx);

TransportRx::TransportRx() {
    endServiceEvent = NULL;
    sendFeedbackEvent = NULL;
}

TransportRx::~TransportRx() {
    cancelAndDelete(endServiceEvent);
    cancelAndDelete(sendFeedbackEvent);
    while (!rxBuffer.isEmpty()) {
        delete rxBuffer.pop();
    }
    while (!ackQueue.isEmpty()) {
        delete ackQueue.pop();
    }
}

void TransportRx::initialize() {
    endServiceEvent = new cMessage("endService");
    rxBuffer.setName("rxBuffer");                  // nombre del buffer para el inspector
    bufferSize = par("bufferSize");                // leer capacidad máxima del .ned
    rwnd = bufferSize;
    droppedPackets = 0;
    bufferSizeVector.setName("bufferSize");        // nombre del vector de ocupación
    packetDropVector.setName("packetDrops");       // nombre del vector de descartes
    bufferSizeVector.record(rxBuffer.getLength()); // al inicio el buffer está vacío
    sendFeedbackEvent = new cMessage("sendFeedback");
    ackQueue.setName("ackQueue");
    // TODO: ¿Hay que darle un tamaño a ackQueue?
}

void TransportRx::finish() {
    recordScalar("Dropped packets", droppedPackets);
}

void TransportRx::handleMessage(cMessage *msg) {

    // si llegó el evento interno de fin de servicio, despachar el siguiente paquete al sink
    if (msg == endServiceEvent) {
        if (!rxBuffer.isEmpty()) {
            // sacar el próximo paquete del buffer
            cPacket *pkt = check_and_cast<cPacket *>(rxBuffer.pop());
            // calcular cuánto tarda en transmitirse por el canal hacia el sink
            cChannel *channel = gate("toApp")->findTransmissionChannel();
            simtime_t serviceTime = channel ? channel->calculateDuration(pkt) : SIMTIME_ZERO;
            // enviar al sink
            send(pkt, "toApp");
            // registrar ocupación del buffer tras el despacho
            bufferSizeVector.record(rxBuffer.getLength());
            // programar el próximo despacho cuando termine este
            scheduleAt(simTime() + serviceTime, endServiceEvent);
            // actualizar rwnd y notificar al transmisor
            rwnd = bufferSize - rxBuffer.getLength();
        }
        return;
    }

    // si llegó el evento de envío de feedback, despachar el próximo ACK
    if (msg == sendFeedbackEvent) {
        if (!ackQueue.isEmpty()) {
            // verificar si el canal de retorno está ocupado
            cChannel *channel = gate("toNetwork")->findTransmissionChannel();
            if (channel && channel->isBusy()) {
                // reintentar cuando el canal se libere
                scheduleAt(channel->getTransmissionFinishTime(), sendFeedbackEvent);
                return;
            }
            // sacar el próximo ACK de la cola de feedback
            TransportPkt *ack = check_and_cast<TransportPkt*>(ackQueue.pop());
            // enviar el ACK al transmisor
            send(ack, "toNetwork");
            // si quedan ACKs en la cola, schedulear el próximo envío inmediatamente
            if (!ackQueue.isEmpty()) {
                scheduleAt(simTime(), sendFeedbackEvent);
            }
        }
        return;
    }

    // llegó un paquete de datos desde la red

    // si el buffer está lleno, descartar el paquete y registrar la pérdida
    if (rxBuffer.getLength() >= bufferSize) {
        droppedPackets++;
        packetDropVector.record(droppedPackets);
        delete msg;
        return;
    }

    // hay espacio: encolar el paquete
    rxBuffer.insert(msg);

    // registrar ocupación del buffer tras la inserción
    bufferSizeVector.record(rxBuffer.getLength());

    // actualizar rwnd: espacio libre restante en el buffer
    rwnd = bufferSize - rxBuffer.getLength();

    // leer el bit ECN del paquete recibido
    TransportPkt *dataPkt = check_and_cast<TransportPkt*>(msg);
    bool congestionMarked = dataPkt->getEcn();

    // crear ACK con información de control de flujo y congestión
    TransportPkt *ack = new TransportPkt("ACK");
    ack->setByteLength(20);
    ack->setType(ACK);
    ack->setRwnd(rwnd);
    ack->setEcn(congestionMarked);

    // encolar el ACK y schedulear su envío
    ackQueue.insert(ack);
    if (!sendFeedbackEvent->isScheduled()) {
        cChannel *channel = gate("toNetwork")->findTransmissionChannel();
        simtime_t when = simTime();
        if (channel && channel->isBusy()) {
            when = channel->getTransmissionFinishTime();
        }
        scheduleAt(when, sendFeedbackEvent);
    }

    // si el servidor está idle, arrancar el despacho inmediatamente
    if (!endServiceEvent->isScheduled()) {
        scheduleAt(simTime(), endServiceEvent);
    }
}

#endif /* TRANSPORTRX */
