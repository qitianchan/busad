/**
 * Created by qitian on 2015/10/29.
 */
UserApp.factory('District', function(Restangular) {
    var district;
    district = {

        getList: function() {
            return Restangular
                .one('districts')
                .getList();
        },
        create: function(data) {
            return Restangular
                .one('districts')
                .customPOST(data);
        }
    };
    return district;
});