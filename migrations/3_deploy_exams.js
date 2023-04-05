const exams=artifacts.require('exams');

module.exports=function(deployer){
    deployer.deploy(exams);
}