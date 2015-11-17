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

        $scope.waiting = false;
        $scope.visible = false;

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
            $scope.waiting = true;

            Bus.one(bus.id).customPUT(data).then(function(ret){
                $scope.waiting = false;
                toaster.pop('success', '保存成功', '');
            },function(ret){
                toaster.pop('error', '保存失败', '数据冲突');
                return ''
            })
            var hel = 'haha';
        };

        /* TODO：save, edit del add */

}]);
}();
