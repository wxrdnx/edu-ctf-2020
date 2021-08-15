const config = require('./config')
const Web3 = require('web3')

async function main() {
    if (process.argv.length !== 3) {
        console.error('please provide the address of your Bet contract');
        return;
    }
    let addr = process.argv[2];
    let web3 = new Web3(config.network);
    await web3.eth.getStorageAt(addr, 1).then((seed_hex) => {
        let seed = parseInt(seed_hex, 16);
        console.log(seed);
    });
}
main();
