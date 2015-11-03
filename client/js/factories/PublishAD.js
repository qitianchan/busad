/**
 * Created by qitian on 2015/10/29.
 */
UserApp.factory('PublishAD', function(Restangular) {
    var publishAd;
    publishAd = {
        publish: function(data) {
            return Restangular
                .one('publish')
                .customPOST(data);
        }
    };
    return publishAd;
});