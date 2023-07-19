Sure! Here's an example of how you can use the `autorelay` module to automatically find and connect to relays:

```go
package main

import (
	"context"
	"log"

	"github.com/libp2p/go-libp2p"
	"github.com/libp2p/go-libp2p/autorelay"
	"github.com/libp2p/go-libp2p/p2p/host/basic"
)

func main() {
	// Create a basic host
	h, err := basic.NewHost(context.Background(), autorelay.NewAutoRelayHostOption())
	if err != nil {
		log.Fatal(err)
	}

	// Create an AutoRelay instance
	ar, err := autorelay.NewAutoRelay(h)
	if err != nil {
		log.Fatal(err)
	}

	// Start the AutoRelay
	ar.Start()

	// Connect to a peer via the relay
	peerAddr, _ := ma.NewMultiaddr("/ip4/127.0.0.1/tcp/1234/p2p/QmPeerID")
	peerInfo, _ := peer.AddrInfoFromP2pAddr(peerAddr)
	if err := h.Connect(context.Background(), *peerInfo); err != nil {
		log.Fatal(err)
	}

	// Wait for the connection to be established
	<-h.Network().ConnectednessEvent(peerInfo.ID).Connected

	log.Println("Connected to peer via relay!")
}
```

In this example, we create a basic host and pass it to the `NewAutoRelayHostOption` function to enable autorelay functionality. Then, we create an `AutoRelay` instance and start it. Finally, we connect to a peer using the host's `Connect` method, and wait for the connection to be established.

Note that you'll need to replace `QmPeerID` with the actual peer ID of the peer you want to connect to.

I hope this helps! Let me know if you have any further questions.