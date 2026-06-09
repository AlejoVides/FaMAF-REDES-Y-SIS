#ifndef LNK
#define LNK

#include <string.h>
#include <omnetpp.h>
#include <packet_m.h>

using namespace omnetpp;

class Lnk: public cSimpleModule {
private:
    cQueue buffer;
    cMessage *endServiceEvent;
    simtime_t serviceTime;
    cOutVector bufferSizeVector;
    simtime_t totalBusyTime;
public:
    Lnk();
    virtual ~Lnk();
protected:
    virtual void initialize();
    virtual void finish();
    virtual void handleMessage(cMessage *msg);
};

Define_Module(Lnk);

#endif /* LNK */

Lnk::Lnk() {
    endServiceEvent = NULL;
}

Lnk::~Lnk() {
    cancelAndDelete(endServiceEvent);
}

void Lnk::initialize() {
    endServiceEvent = new cMessage("endService");
    bufferSizeVector.setName("Buffer Size");
    totalBusyTime = 0;
    par("bufferLoad").setIntValue(0);
}

void Lnk::finish() {
    // Record statistics
    recordScalar("Link utilization", totalBusyTime / simTime());
}

void Lnk::handleMessage(cMessage *msg) {

    if (msg == endServiceEvent) {
        if (!buffer.isEmpty()) {
            // dequeue
            Packet* pkt = (Packet*) buffer.pop();
            bufferSizeVector.record(buffer.getLength());
            // update buffer load parameter
            par("bufferLoad").setIntValue(buffer.getLength());
            // send
            send(pkt, "toOut$o");
            serviceTime = pkt->getDuration();
            scheduleAt(simTime() + serviceTime, endServiceEvent);
            // accumulate busy time for link utilization
            totalBusyTime += serviceTime;
        }
    } else { // msg is a packet
        if (msg->arrivedOn("toNet$i")) {
            // enqueue
            buffer.insert(msg);
            bufferSizeVector.record(buffer.getLength());
            // update buffer load parameter
            par("bufferLoad").setIntValue(buffer.getLength());
            // if the server is idle
            if (!endServiceEvent->isScheduled()) {
                // start the service now
                scheduleAt(simTime(), endServiceEvent);
            }
        } else {
            //msg is from out, send to net
            send(msg, "toNet$o");
        }
    }
}
