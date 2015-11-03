/**
 * Created by lenovo on 2015/10/30.
 */
UserApp.filter('busFilter', function(routeSelectedArray){
    return function(busArray){
        var array = [];
        angular.forEach(routeSelectedArray, function(route){
            angular.forEach(busArray, function(bus){
                if(bus.route_id == route.id){
                    array.push(bus)
                }
            })
        });
        return array;
    }

});