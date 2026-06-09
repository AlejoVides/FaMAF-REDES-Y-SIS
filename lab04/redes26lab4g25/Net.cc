#ifndef NET
#define NET

#include <string.h>
#include <omnetpp.h>
#include <packet_m.h>

using namespace omnetpp;

class Net: public cSimpleModule {
private:
    int forwardedPackets;
    int numNodes;

    int shortestPath(int source, int destination, int direction);
    int selectOutPort(int source, int destination);
public:
    Net();
    virtual ~Net();
protected:
    virtual void initialize();
    virtual void finish();
    virtual void handleMessage(cMessage *msg);
};

Define_Module(Net);

#endif /* NET */

Net::Net() {
}

Net::~Net() {
}

void Net::initialize() {
    forwardedPackets = 0;
    // Obtengo el numero total de nodos del anillo
    cModule *network = getParentModule()->getParentModule();
    numNodes = network->getSubmoduleVectorSize("node");
}

void Net::finish() {
    // Record statistics
    recordScalar("Forwarded packets", forwardedPackets);
}

int Net::shortestPath(int source, int destination, int direction) {
    
    if (direction == 1) {
        // Clockwise: hacia nodos mayores
        if (destination > source)   return destination - source;
        else                        return numNodes - source + destination;

    } else {
        // Counter-clockwise: hacia nodos menores
        if (source > destination)   return source - destination;
        else                        return source + numNodes - destination;
    }
}

int Net::selectOutPort(int source, int destination) {

    int myIndex = getParentModule()->getIndex();
    
    // Calculo la distancia en ambas direcciones
    int distClockwise = shortestPath(myIndex, destination, 1);        // puerto 1
    int distCounterClockwise = shortestPath(myIndex, destination, 0); // puerto 0
    
    int selectedPort;
    
    if (distClockwise < distCounterClockwise) selectedPort = 1;
    else if (distCounterClockwise < distClockwise) selectedPort = 0;

    else {
        // Desempatamos por congestion
        cModule *clockwise = getParentModule()->getSubmodule("lnk", 1);
        cModule *counterClockwise = getParentModule()->getSubmodule("lnk", 0);

        int loadCW = clockwise->par("bufferLoad");
        int loadCCW = counterClockwise->par("bufferLoad");

        if (loadCW <= loadCCW) selectedPort = 1;
        else selectedPort = 0;
    }
    return selectedPort;
}

void Net::handleMessage(cMessage *msg) {

    // All msg (events) on net are packets
    Packet *pkt = (Packet *) msg;
    int myIndex = getParentModule()->getIndex();

    // If this node is the final destination, send to App
    if (pkt->getDestination() == myIndex) {
        send(msg, "toApp$o");
    } else {
        int outPort = selectOutPort(pkt->getSource(), pkt->getDestination());
        
        if (pkt->getSource() != myIndex) {
            forwardedPackets++;
        }
        pkt->setHopCount(pkt->getHopCount() + 1);
        send(msg, "toLnk$o", outPort);
    }
}
