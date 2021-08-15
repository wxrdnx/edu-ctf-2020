# HW3 writeup

## Bet
### Description
本題在 ropsten 測試鏈的 `0x8e0a809B1f413deB6427535cC53383954DBF8329` 位址上跑一個 `BetFactory` 的智能合約。該和約會根據不同的 sender 建立不同的 `Bet` 合約。`Bet` 合約繼承 `Challenge` 合約，其中 `Challenge` 合約中有一個 `player` 變數，當 `Bet` 合約建立時，`player` 的變數會存入 `msg.sender` 。另外 `Challenge` 合約裡有一個 `onlyPlayer` 的 modifier，他會去檢查 sender 是否是 player 本人。我們可以看到 `Bet` 合約中有一個 `bet` 函式可以玩賭博遊戲。`bet` 函式有 `onlyPlayer` 的 modifier，因此只有當前的使用這可以賭錢（也就是說沒有人能幫令一個人解題）。

### Analysis
在`bet` 函式中，我們可以看到如果我們賭的數字和 `getRandom` 函式產生出來的僞隨機數一樣的話，它會把所有合約中的所有 :moneybag: 送給我 。`getRandom` 函式看似是隨機的，但實則不然。該 PRNG 是依靠最後一個 block 的 hash 值去 xor 一個 seed 作為隨機數的。

第一點，seed 是長在合約上的。在 Solidity 中，private 意思是指「僅對智能合約範圍是私有的」，這意味著它們不能從其他智能合約訪問的。但是，任何人都可以在區塊鏈外部自由讀取它們的值。因此某種意義上他們不是實質意義上的 private。理論上，這個世界上擁有瀏覽區塊鏈能力的任何人都可以看到你的 private 變量。實務上，我們可以呼叫 `getStorageAt` 這個函數把合約的 storage 傾倒出來，進而得到 seed 。

```javascript
...
await web3.eth.getStorageAt(addr, 1).then((seed_hex) => {
    let seed = parseInt(seed_hex, 16);
    console.log(seed);
});
...
```

第二點，最後一個 block 的 hash 值，亦即 `block.blockhash(block.number - 1)`，對同一個 block chain 的所有 transaction 結果都會是相同的。由此可知，我們可以在自己的合約中佈署相同 getRand 函數，調用它後所產生的隨機數會和另一端產生的隨機數相同。

```solidity
...
uint private seed;
...
function setSeed(uint seed_) public {
    seed = seed_;
}
function getRandom () internal returns(uint) {
    uint rand = seed ^ uint(blockhash(block.number - 1));
    seed ^= block.timestamp;
    return rand;
}
...
```
### Exploitation

由以上的分析可知，解這題的方法是使用 remix IDE 自行佈署一個智能合約。合約的 solidity 程式碼在 `Solve.sol` 中可以看到。
詳細步驟如下：

1. 在 remix IDE 創建檔案 `Solve.sol` 。將 `Solve.sol` 複製到 IDE 中。之後，點選 `Compile Solve.sol` 。編譯完 `Solve.sol` 後，將 Environment 設定為 `Injected Web` 以及 Contract 設定為 `Solve - browser.Sol`。 最後，按下 `Deploy` 將合約佈署到 ropsten 鏈中。
2. 呼叫自己寫的合約上的 `create` 函數。`create` 函數會呼叫 BetFactory 合約中的 `create` 函數建構題目。`address_factory` 理應填入 `BetFactory` 的位址，亦即 `0x8e0a809B1f413deB6427535cC53383954DBF8329`。
3. 我們可以執行 `node getseed.js <你佈署的 Solve 合約的位址>` 撈出 `seed` 的值，然後利用自己寫的合約上的 `setSeed` 函數設定 seed 的值。
4. 呼叫自己寫的合約上的 `run` 函數。`run` 函數中有我們自己寫的和 `Bet` 中相同的 `getRand` 函數。`run` 函數會利用 `getRand` 以及撈到的 `seed` 產生可預測的隨機數。最後，`run` 函數會呼叫 `Bet` 中的 `bet` 函數來賭錢。這裏`address_target` 應該填入 `BetFactory` 幫你創好的 `Bet` 合約的位置。
5. 理論上你給的隨機數應該是對的，然後合約的 :moneybag: 會全部被你挖走。最後呼叫 `validate` 函數，填入 nonce 後就能取得 flag 了。
