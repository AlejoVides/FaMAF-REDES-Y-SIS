
#ifndef QUEUE
#define QUEUE

#include <string.h>
#include <omnetpp.h>
#include "TransportPkt_m.h"

using namespace omnetpp;

class Queue: public cSimpleModule {
private:
    cQueue buffer;
    cMessage *endServiceEvent;
    int bufferSize;
    long droppedPackets;
    cOutVector bufferSizeVector;
    cOutVector packetDropVector;
public:
    Queue();
    virtual ~Queue();
protected:
    virtual void initialize();
    virtual void finish();
    virtual void handleMessage(cMessage *msg);
};

Define_Module(Queue);

Queue::Queue() {
    endServiceEvent = NULL;
}

Queue::~Queue() {
    cancelAndDelete(endServiceEvent);
    while (!buffer.isEmpty()) {
        delete buffer.pop();
    }
}

void Queue::initialize()
{
    buffer.setName("buffer");

    endServiceEvent = new cMessage("endService");

    bufferSize = par("bufferSize");
    droppedPackets = 0;

    bufferSizeVector.setName("bufferSize");
    packetDropVector.setName("packetDrops");
}

void Queue::finish() {
    recordScalar("Dropped packets", droppedPackets);
}

void Queue::handleMessage(cMessage *msg) {

    if (msg == endServiceEvent) {
        if (!buffer.isEmpty()) {
            cPacket *pkt = check_and_cast<cPacket *>(buffer.pop());

            // marcar congestión si el buffer supera el 80% de su capacidad
            TransportPkt *tpkt = dynamic_cast<TransportPkt*>(pkt);
            if (tpkt && buffer.getLength() > bufferSize * 0.8) {
                tpkt->setEcn(true);
            }

            cChannel *channel = gate("out")->findTransmissionChannel();
            simtime_t serviceTime = channel ? channel->calculateDuration(pkt) : SIMTIME_ZERO;
            send(pkt, "out");
            bufferSizeVector.record(buffer.getLength());
            scheduleAt(simTime() + serviceTime, endServiceEvent);
        }
        return;
    }

    // overflow check MUST happen before insert
    if (buffer.getLength() >= bufferSize) {
        droppedPackets++;
        packetDropVector.record(droppedPackets);
        delete msg;
        return;
    }

    buffer.insert(msg);
    bufferSizeVector.record(buffer.getLength());

    if (!endServiceEvent->isScheduled()) {
        scheduleAt(simTime(), endServiceEvent);
    }
}

#endif /* QUEUE */
