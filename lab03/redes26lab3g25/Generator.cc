#ifndef GENERATOR
#define GENERATOR

#include <string.h>
#include <omnetpp.h>
#include "PacketKind.h"

using namespace omnetpp;

class Generator : public cSimpleModule {
private:
    cMessage *sendMsgEvent;
    cStdDev transmissionStats;
    cOutVector packetGenVector;
    long generatedPackets;
public:
    Generator();
    virtual ~Generator();
protected:
    virtual void initialize();
    virtual void finish();
    virtual void handleMessage(cMessage *msg);
};
Define_Module(Generator);

Generator::Generator() {
    sendMsgEvent = NULL;

}

Generator::~Generator() {
    cancelAndDelete(sendMsgEvent);
}

void Generator::initialize() {

    packetGenVector.setName("packetGen");
    generatedPackets = 0;
    transmissionStats.setName("TotalTransmissions");
    // create the send packet
    sendMsgEvent = new cMessage("sendEvent");
    // schedule the first event at random time
    scheduleAt(par("generationInterval"), sendMsgEvent);
}

void Generator::finish() {
    recordScalar("Generated packets", generatedPackets);
}

void Generator::handleMessage(cMessage *msg) {

    cPacket *pkt = new cPacket("packet");
    packetGenVector.record(1);
    generatedPackets++;
    pkt->setByteLength(par("packetByteSize"));
    pkt->setKind(DATA);
    send(pkt, "out");

    simtime_t nextTime = simTime() + par("generationInterval");
    scheduleAt(nextTime, sendMsgEvent);
}

#endif /* GENERATOR */
