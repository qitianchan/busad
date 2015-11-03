/**
 * Created by qitian on 2015/10/29.
 */
UserApp.factory('Route', function(Restangular) {
    var Route;
    Route = {
        getList: function() {
            return Restangular
                .one('routes')
                .getList();
        },
        create: function(data) {
            return Restangular
                .one('routes')
                .customPOST(data);
        }
    };
    return Route;
});