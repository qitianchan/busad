/**
 * Created by qitian on 2016/5/12 0012.
 */

(function(){
   UserApp.factory('Group', function(Restangular) {
       var service = Restangular.service('group');
       service.validateData = function() {

       };
       return service;
   })
}());
