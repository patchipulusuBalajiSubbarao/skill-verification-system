// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract exams {

    // contract variables
    address[] _usernames;
    address[] _examowners;
    uint[] _examids;
    uint[] _marks;
    uint[] _statuses; // 0 - Not Yet Started, 1 - Submitted, 2 - Evaluated
    string[] _examhash;

    function allocateExam(address username,address examowner,uint examid) public {
        _usernames.push(username);
        _examowners.push(examowner);
        _examids.push(examid);
        _marks.push(0);
        _statuses.push(0);
        _examhash.push("");
    }

    function attemptExam(address username,uint examid,string memory examhash) public {

        uint i;
        for(i=0;i<_usernames.length;i++) {
            if(_usernames[i]==username && examid==_examids[i]) {
                _statuses[i]=1;
                _examhash[i]=examhash;
            }
        }

    }

    function viewExams() public view returns(address[] memory,address[] memory, uint[] memory, uint[] memory,uint[] memory, string[] memory) {
        return(_usernames,_examowners,_examids,_marks,_statuses,_examhash);
    }

    function allocateMarks(address username,uint examid,uint marks) public {

        uint i;
        for(i=0;i<_usernames.length;i++){
            if(_usernames[i]==username && _examids[i]==examid) {
                _marks[i]=marks;
                _statuses[i]=2;
            }
        }
    }    
}