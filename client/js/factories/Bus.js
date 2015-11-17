
/**
 * Created by qitian on 2015/10/29.
 */
(function() {
    UserApp.factory('Bus', function(Restangular) {
    //var Bus;
    //Bus = {
    //
    //    getList: function() {
    //        return Restangular
    //            .one('buses')
    //            .getList();
    //    },
    //    create: function(data) {
    //        return Restangular
    //            .one('buses')
    //            .customPOST(data);
    //    },
    //    put: function(data){
    //        return Restangular
    //            .one('buses')
    //            .customPUT(data)
    //    }
    //};
    //return Bus;

        var service = Restangular.service('buses');
        service.validateData = function(student) {
            // validate student data
        }

        return service;

    });

}());
