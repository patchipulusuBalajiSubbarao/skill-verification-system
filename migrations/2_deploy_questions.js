const questions=artifacts.require('questions');

module.exports=function(deployer){
    deployer.deploy(questions);
}