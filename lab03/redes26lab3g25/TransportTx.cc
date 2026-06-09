#ifndef TRANSPORTTX
#define TRANSPORTTX

#include <omnetpp.h>
#include <algorithm>        // Para std::min y std::max
#include "TransportPkt_m.h" // Cabecera autogenerada del archivo .msg
#include "PacketKind.h"

using namespace omnetpp;

class TransportTx : public cSimpleModule {
private:
    double cwnd;              // Ventana de Congestión (AIMD)
    double rwnd;              // Ventana del Receptor (Control de Flujo)
    long inFlight;            // Paquetes en vuelo (enviados sin ACK)
    long nextSeq;             // Próximo número de secuencia a asignar

    // ===== BUFFERS Y TIMERS =====
    cQueue txBuffer;          // Buffer interno para almacenar lo que manda el Generator
    cMessage *sendTimer;      // Evita colisiones de eventos si el canal está ocupado

    // ===== MONITOREO =====
    cOutVector cwndVector;
    cOutVector inFlightVector;
    cOutVector rwndVector;
    cOutVector bufferSize;
    cOutVector effectiveWindowVector;

public:
    TransportTx();
    virtual ~TransportTx();
protected:
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
    virtual void finish() override;

    void tryToSend();
    void onDataFromApp(cPacket *pkt);
    void onAckReceived(TransportPkt *ack); // Cambiado al tipo estricto del archivo .msg
};

Define_Module(TransportTx);

TransportTx::TransportTx() {
    sendTimer = NULL;
}

TransportTx::~TransportTx() {
    cancelAndDelete(sendTimer);
    while (!txBuffer.isEmpty()) {
        delete txBuffer.pop();
    }
}

void TransportTx::initialize() {
    cwnd = par("cwndInit").doubleValue();
    rwnd = 200; // Inicia en un valor grande hasta recibir el primer ACK real
    inFlight = 0;
    nextSeq = 0; // Primer paquete arranca con secuencia 0

    sendTimer = new cMessage("sendTimer");

    cwndVector.setName("cwnd");
    inFlightVector.setName("inFlight");
    rwndVector.setName("rwnd");
    bufferSize.setName("bufferSize");
    effectiveWindowVector.setName("effectiveWindow");

    cwndVector.record(cwnd);
    inFlightVector.record(inFlight);
    rwndVector.record(rwnd);
    bufferSize.record(txBuffer.getLength()); // al inicio el buffer está vacío
    effectiveWindowVector.record(std::min(cwnd, rwnd));
}

void TransportTx::finish() {
}

void TransportTx::handleMessage(cMessage *msg) {
    if (msg == sendTimer) {
        // el canal se liberó, reintentar envío
        tryToSend();
    }
    else if (msg->getArrivalGate() == gate("fromApp")) {
        // llegó un paquete del Generator, encolar y tratar de enviarlo
        onDataFromApp(check_and_cast<cPacket*>(msg));
    }
    else if (msg->getArrivalGate() == gate("fromNetwork")) {
        // llegó un ACK del receptor, actualizar ventanas
        onAckReceived(check_and_cast<TransportPkt*>(msg));
    }
}

void TransportTx::onDataFromApp(cPacket *pkt) {
    // Guardamos el paquete que viene de la aplicación en la cola interna
    txBuffer.insert(pkt);
    bufferSize.record(txBuffer.getLength());
    tryToSend();
}

void TransportTx::tryToSend() {
    while (!txBuffer.isEmpty() && inFlight < std::min(cwnd, rwnd)) {
        // si el canal está ocupado, reintentar cuando se libere
        cChannel *ch = gate("toNetwork")->getTransmissionChannel();
        if (ch && ch->isBusy()) {
            if (!sendTimer->isScheduled()) {
                scheduleAt(ch->getTransmissionFinishTime(), sendTimer);
            }
            break; 
        }

        // Sacamos el paquete genérico de la cola de la aplicación
        cPacket *appPkt = check_and_cast<cPacket*>(txBuffer.pop());
        bufferSize.record(txBuffer.getLength());

        // ===== CREACIÓN DEL PAQUETE PROPIO USANDO LAS CLASES DEL .MSG =====
        TransportPkt *pkt = new TransportPkt(appPkt->getName());
        pkt->setByteLength(appPkt->getByteLength()); // tamaño del payload original (overhead de cabecera despreciable)
        pkt->setType(DATA);
        pkt->setSeq(nextSeq++);       // Asignamos secuencia e incrementamos para el próximo
        pkt->setTimestamp(simTime()); // Guardamos el tiempo de salida (útil para delay/RTT)

        // Eliminamos el mensaje original de la aplicación ya que fue empaquetado/reemplazado
        delete appPkt; 

        send(pkt, "toNetwork");
        inFlight++; 

        inFlightVector.record(inFlight);
        effectiveWindowVector.record(std::min(cwnd, rwnd));
    }
}

void TransportTx::onAckReceived(TransportPkt *ack) {
    // ===== USO DE GETTERS EXCLUSIVOS DEL ARCHIVO .MSG =====
    rwnd = ack->getRwnd(); 
    bool ecnBit = ack->getEcn();

    if (inFlight > 0) inFlight--;
    
    // ===== LÓGICA AIMD (Additive Increase Multiplicative Decrease) =====
    if (ecnBit == false) cwnd += 1.0 / cwnd;
    else cwnd = std::max(1.0, cwnd / 2.0);

    cwndVector.record(cwnd);
    rwndVector.record(rwnd);
    inFlightVector.record(inFlight);
    effectiveWindowVector.record(std::min(cwnd, rwnd));

    // Liberar la memoria para evitar fugas (criterio estricto de corrección)
    delete ack;

    // Intentar meter más datos al liberarse la ventana o modificarse cwnd
    tryToSend();
}

#endif /* TRANSPORTTX */
