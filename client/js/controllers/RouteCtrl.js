+function(){
  UserApp.controller('RouteCtrl', ['$scope', '$filter', 'District', 'Route','Bus','toaster',
    function($scope, $filter, District, Route, Bus, toaster) {
        $scope.busSelected = true;
        $scope.routeSelected = false;
        $scope.districtSelected = false;

        $scope.tabSelect = function(i){
            $scope.busSelected = (i == 1);
            $scope.routeSelected = (i == 2);
            $scope.districtSelected = (i == 3);
        };

        Bus.getList().then(function(ret){
            $scope.buses = ret
        });


        Route.getList().then(function(ret){
            $scope.routes = ret
        });

        District.getList().then(function(ret){
            $scope.districts = ret
        });

        $scope.showRoute = function(bus){
            var selected = [];
            if(bus.route_id) {
                selected = $filter('filter')($scope.routes, {id: bus.route_id});
            }
            return selected.length ? selected[0].route_name : 'Not set'
        };

        $scope.showDistrict = function(route){
            var selected = [];
            if(route.district_id) {
                selected = $filter('filter')($scope.districts, {id: route.district_id});
            }
            return selected.length ? selected[0].district_name : 'Not set'
        };

        $scope.checkPlateNum = function(data, bus){
          if(data==='undefined' || data == null){
              return '不能为空值'
          }
        };

        $scope.saveBus = function(data, bus){
            Bus.
            toaster.pop('error', '数据错误', 'hello');
            return ''
        };

        /* TODO：save, edit del add */

}]);
}();
