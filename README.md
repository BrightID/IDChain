# Idchain

Idchain is a fork of the [official Golang implementation of the Ethereum protocol](https://github.com/ethereum/go-ethereum) with a small change to burn gas fees instead of awarding them to the block sealers.

## Joining the Idchain Network

### Building on Ubuntu

```shell
$ sudo snap install go --classic
$ sudo apt-get install -y build-essential
$ git clone https://github.com/BrightID/idchain.git
$ cd idchain
$ make geth
$ sudo ln -sf $PWD/build/bin/geth /usr/bin/geth
```

### Running a Node

```shell
$ cd ~
$ mkdir node
$ cd node
# Initializing the node by genesis file
$ wget http://idchain.brightid.org/files/idchain-genesis.json
$ geth --datadir . init idchain-genesis.json
# Setting static peers
$ wget http://idchain.brightid.org/files/static-nodes.json
# Running the node
$ geth --datadir . --networkid 74
```

_The `node` folder will play as `datadir` for `geth` and can be anywhere, but it should not be inside `idchain` that we created and built `geth` in previous step._


### Adding a Validator

#### Proposing New Validator to Network
To join the network as validator, half of the current validators should [use clique api to propose the new validator](https://geth.ethereum.org/docs/rpc/ns-clique#clique_propose) to the network.

```shell
$ cd ~/node
$ geth attach geth.ipc
Welcome to the Geth JavaScript console!

> clique.propose("0x...", true)
```
After the proposal approved, the new validator address should be appeared in the `sealersActivity` in response of `clique.status()`.
```shell
> clique.status()
{
  inturnPercent: 66.6666,
  numBlocks: 64,
  sealerActivity: {
    VALIDATOR1_ADDRESS: 32,
    VALIDATOR2_ADDRESS: 32,
    NEW_VALIDATOR1_ADDRESS: 0
  }
}
```
#### Joining the Network as Validator
To join the network as validator, the new validator should import the private key of the address proposed to network in previous step into geth and run the node in mining mode.

```shell
$ cd ~
$ mkdir node
$ cd node
# Initializing the node by genesis file
$ wget http://idchain.brightid.org/files/idchain-genesis.json
$ geth --datadir . init idchain-genesis.json
# Setting static peers
$ wget http://idchain.brightid.org/files/static-nodes.json
# importing the address proposed as validator to network
$ echo "YOUR PRIVATE KEY" > key.priv
$ geth account import --datadir . key.priv
The new account will be encrypted with a passphrase.
Please enter a passphrase now.
Passphrase:
Repeat Passphrase:
Address: {...}
# Creating password file to unlock account using that
$ echo "YOUR PASSPHRASE" > password.txt
$ geth --datadir . --syncmode full --port 30329 --networkid 74 --gasprice 1 --unlock "YOUR ADDRESS" --password password.txt --mine --allow-insecure-unlock
```
_You can remove the password.txt and key.priv files after running the `geth`._

#### Adding the New Validator Address to Static Peers List
It's a good practice to add `enode` address for all validators to `static-nodes.json` file hosted on `http://idchain.brightid.org/files/static-nodes.json` to enable decentralized access to all peers for everyone that want to join the network.
The new validator can find its node id by:
```shell
$ cd ~/node
$ bootnode -nodekey ./geth/nodekey -writeaddress
```
- The format for `enode` address that should be added to `static-nodes.json` is `enode://NODE_ID@ip:port`.
- The standard port for idchain validators will be 30329.
- The new validator should configure the firewall on its server to open port 30329 to enable others to connect its node.
