Sure! Here's an example of how you can use the autorelay module to automatically find and connect to relays:

```go
package main

import (
	"context"
	"fmt"
	"log"

	"github.com/libp2p/go-libp2p"
	"github.com/libp2p/go-libp2p-autorelay"
	"github.com/libp2p/go-libp2p-core/peer"
	ma "github.com/multiformats/go-multiaddr"
)

func main() {
	// Create a new libp2p host
	host, err := libp2p.New(context.Background(), libp2p.EnableAutoRelay())
	if err != nil {
		log.Fatal(err)
	}

	// Get the peer ID of the host
	peerID := host.ID()

	// Get the multiaddress of the host
	hostAddr, _ := ma.NewMultiaddr(fmt.Sprintf("/ipfs/%s", peer.IDB58Encode(peerID)))

	// Print the host's multiaddress
	fmt.Printf("Host address: %s\n", hostAddr)

	// Start the host
	if err := host.Connect(context.Background(), autorelay.DefaultRelays...); err != nil {
		log.Fatal(err)
	}

	// Print the host's connected peers
	fmt.Println("Connected peers:")
	for _, p := range host.Network().Peers() {
		fmt.Printf("- %s\n", p)
	}
}
```

In this example, we create a new libp2p host and enable the autorelay feature by passing `libp2p.EnableAutoRelay()` as an option to `libp2p.New()`. This will automatically find and connect to relays.

We then get the peer ID and multiaddress of the host, and print the host's multiaddress.

Next, we start the host and connect to the default relays provided by the autorelay module using `host.Connect(context.Background(), autorelay.DefaultRelays...)`.

Finally, we print the host's connected peers.

Note that you will need to import the necessary packages (`github.com/libp2p/go-libp2p`, `github.com/libp2p/go-libp2p-autorelay`, `github.com/libp2p/go-libp2p-core/peer`, and `github.com/multiformats/go-multiaddr`) and handle any errors that may occur.