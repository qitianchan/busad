/**
 * Created by qitian on 2015/10/27.
 */

UserApp.service('UserService', UserService=function(Restangular){
    this.getUser = function(){
        var User = Restangular.allUrl('users', 'http://localhost:5000/api/');
        var users = User.getList();
        var hello = 'hello'
    };

});