// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract questions{

    // contract variables
    address[] _usernames;
    string[][] _questions;
    uint[][] _marks;
    uint[] _examids;
    string[] _examnames;

    uint ecount=0;

    mapping(uint=>bool) _exams;

    // function which can add exam
    function addExam(address username,string memory examname,string[] memory question,uint[] memory marks) public {
        
        ecount+=1;
        _examnames.push(examname);
        _usernames.push(username);
        _questions.push(question);
        _marks.push(marks);
        _examids.push(ecount);
    }

    // function which displays all exams
    function viewExams() public view returns(address[] memory,string[][] memory,uint[][] memory,uint[] memory,string[] memory) {
        return(_usernames,_questions,_marks,_examids,_examnames);
    }

}