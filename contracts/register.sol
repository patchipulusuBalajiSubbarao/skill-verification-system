// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract register {
  
  address[] _usernames; // stores the wallet address
  string[] _names;
  string[] _emails;
  string[] _mobiles;
  uint[] _passwords;
  uint[] _roles; // 0 - instructor, 1 - evaluator, 2-candidate, 3-recruiter

  mapping(address=>bool) _users; // avoiding duplicate users

  // INSERT INTO - registering the user
  function registerUser(address username,string memory name, string memory email,string memory mobile,uint password,uint role) public {

    require(!_users[username]); // if it is first time, it will allow

    _users[username]=true;
    _roles.push(role);
    _usernames.push(username);
    _names.push(name);
    _emails.push(email);
    _mobiles.push(mobile);
    _passwords.push(password); // push - inserting data into the contract variables
  }

  // SELECT * - displaying all the user details
  function viewUsers() public view returns(address[] memory,string[] memory,string[] memory email,string[] memory,uint[] memory,uint[] memory) {
    return(_usernames,_names,_emails,_mobiles,_passwords,_roles);
  }

  // function which is called for login
  function loginUser(address username,uint password) public view returns(bool){

    uint i;
    require(_users[username]); // this will block unregistered users

    for(i=0;i<_usernames.length;i++){
      if(_usernames[i]==username && _passwords[i]==password) {
        return true;
      }
    }
    return false;
  }
}
