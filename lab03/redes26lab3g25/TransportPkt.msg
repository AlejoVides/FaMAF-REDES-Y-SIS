// TransportPkt.msg
// Definición del paquete personalizado para la Capa de Transporte (Parte 2)

packet TransportPkt {
    long seq;          // Número de secuencia para identificar el paquete de datos
    int type;          // Tipo de paquete: 1 = DATA, 2 = ACK
    double rwnd;       // Ventana del Receptor (Control de Flujo - Espacio libre en el buffer)
    bool ecn;          // Bit de notificación explícita de congestión (Control de Congestión)
    simtime_t timestamp; // Momento exacto en que se creó/envió para medir demoras (Punto 3)
}
