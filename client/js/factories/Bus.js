/**
 * Created by qitian on 2015/10/29.
 */
UserApp.factory('Bus', function(Restangular) {
    var Bus;
    Bus = {

        getList: function() {
            return Restangular
                .one('buses')
                .getList();
        },
        create: function(data) {
            return Restangular
                .one('buses')
                .customPOST(data);
        }
    };
    return Bus;
});