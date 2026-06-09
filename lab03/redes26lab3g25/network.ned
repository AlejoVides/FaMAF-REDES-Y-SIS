simple Generator
{
    parameters:
        volatile double generationInterval; // sec
        int packetByteSize;
        @display("i=block/source");
    gates:
        output out;
}

simple Queue
{
    parameters:
        int bufferSize;
        @display("i=block/queue;q=buffer");
    gates:
        input in;
        output out;
}

simple Sink
{
    parameters:
        @display("i=block/sink");
    gates:
        input in;
}

simple TransportTx
{
    parameters:
        int bufferSize;
        double cwndInit;
        @display("i=block/process");
    gates:
        input fromApp;      // paquetes de datos desde el Generator
        output toNetwork;   // paquetes de datos hacia la cola intermedia
        input fromNetwork;  // feedback del receptor
}

simple TransportRx
{
    parameters:
        int bufferSize;
        @display("i=block/process");
    gates:
        output toApp;       // paquetes de datos hacia el Sink
        input fromNetwork;  // paquetes de datos desde la cola intermedia
        output toNetwork;   // feedback hacia el transmisor
}

module NodeTx
{
    gates:
        output out;
        input in; // Entrada para feedback
    submodules:
        gen: Generator {
            @display("p=60,60");
        }
        transportTx: TransportTx {
            @display("p=180,90");
        }
    connections:
        gen.out --> transportTx.fromApp;
        transportTx.toNetwork --> out;
        in --> transportTx.fromNetwork;
}

module NodeRx
{
    parameters:
        double rxToSinkDatarate @unit(bps) = default(1Mbps);
    gates:
        input in;
        output out; // Salida para feedback
    submodules:
        sink: Sink {
            @display("p=180,60");
        }
        transportRx: TransportRx {
            @display("p=60,90");
        }
    connections:
        in --> transportRx.fromNetwork;
        transportRx.toApp --> { datarate = parent.rxToSinkDatarate; } --> sink.in;
        transportRx.toNetwork --> out;
}

network Network
{
    parameters:
        double txToQueueDatarate @unit(bps) = default(1Mbps);
        double queueToRxDatarate @unit(bps) = default(1Mbps);
        double feedbackDatarate @unit(bps) = default(1Mbps);
        double linkDelay @unit(s) = default(100us);
        @display("bgl=2");
    submodules:
        nodeTx: NodeTx {
            @display("p=100,100;i=device/pc");
        }
        queue: Queue {
            @display("p=300,50;i=block/queue"); // Línea superior (paquetes de datos)
        }
        feedbackQueue: Queue {
            @display("p=300,150;i=block/queue"); // Línea inferior (feedback)
        }
        nodeRx: NodeRx {
            @display("p=500,100;i=device/pc");
        }
    connections:
        // Camino de IDA (paquetes de datos)
        nodeTx.out --> { datarate = parent.txToQueueDatarate; delay = parent.linkDelay; } --> queue.in;
        queue.out --> { datarate = parent.queueToRxDatarate; delay = parent.linkDelay; } --> nodeRx.in;

        // Camino de VUELTA (feedback)
        nodeRx.out --> { datarate = parent.feedbackDatarate; delay = parent.linkDelay; } --> feedbackQueue.in;
        feedbackQueue.out --> { datarate = parent.feedbackDatarate; delay = parent.linkDelay; } --> nodeTx.in;
}
