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
        $scope.buses = [];
        $scope.routes = [];
        $scope.districts = [];
        Bus.getList().then(function(ret){
            $scope.buses = ret;
            $scope.original_buses = angular.extend(ret);

        });


        Route.getList().then(function(ret){
            $scope.routes = $scope.original_routes =ret
        });

        District.getList().then(function(ret){
            $scope.districts = $scope.original_districts = ret
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

        $scope.saveBus = function(data, bus, index){
            $scope.waiting = true;
            var originData = {};
            originData.plate_number = bus.plate_number;
            originData.light_number = bus.light_number;
            originData.route_id = bus.route_id;
            originData.eui = bus.eui;

            if(bus.id){
                Bus.one(bus.id).customPUT(data).then(function(ret){
                $scope.waiting = false;
                toaster.pop('success', '保存成功', '');
                },function(ret){
                    //$scope.buses = $scope.original_buses;
                    bus.plate_number = originData.plate_number;
                    bus.light_number = originData.light_number;
                    bus.route_id = originData.route_id;
                    bus.eui = originData.eui;

                    toaster.pop('error', '保存失败', '数据冲突');
                    return ''
                });
            }
            else {


                Bus.post(data).then(function(ret){
                    //$scope.buses.splice(index, 1);
                    bus.id = ret.id;
                toaster.pop('success', '','新建成功');
                }, function(ret){
                    $scope.buses.splice(index, 1);
                    toaster.pop('error', '', '新建失败')
                });
            }

        };

        $scope.addBus = function(){
             $scope.inserted = {
              plate_number: null,
              light_number: null,
              route_id: null,
              eui: null
            };
            $scope.buses.push($scope.inserted);
        };

        $scope.removeBus = function(index, bus){
            if(!bus.id){
                $scope.buses.splice(index, 1)
            }
            Bus.one(bus.id).customDELETE().then(function(ret){
                $scope.buses.splice(index, 1);
                toaster.pop('success', '', '删除成功');
            },function(ret){
                toaster.pop('error', '', '删除失败')
            })
        };

        $scope.saveRoute = function(data, route, index) {
            var originData = {};
            originData.district_id = route.district_id;
            originData.route_name = route.route_name;

            if(route.id){
               Route.one(route.id).customPUT(data).then(
                   function(ret){
                       toaster.pop('success', '', '保存成功')
                   },
                   function(ret){
                       route.district_id = originData.district_id;
                       route.route_name = originData.route_name;
                       toaster.pop('error', '保存失败', '数据冲突')
                   }
               )
            }
            else {
                // 新建item
                Route.post(data).then(function(ret){
                    route.id = ret.id;
                    toaster.pop('success', '', '保存成功')
                },function(ret){
                        $scope.routes.splice(index, 1);
                        toaster.pop('error', '保存失败', '数据冲突')
                    }
                )
            }

        };
        $scope.addRoute = function(){
            $scope.inserted = {
              route_name: null,
              district_id: null
            };
            $scope.routes.push($scope.inserted);
        };

        $scope.removeRoute = function(index, route){
            if(!route.id){
                $scope.routes.splice(index, 1)
            }
            Route.one(route.id).customDELETE().then(function(ret){
                $scope.routes.splice(index, 1);
                toaster.pop('success', '', '删除成功');
            },function(ret){
                toaster.pop('error', '', '删除失败,有其他数据引用此数据')
            })
        };

        // district
        $scope.saveDistrict = function(data, district, index) {
            var originData = {};
            originData.district_name = district.district_name;

            if(district.id){
               District.one(district.id).customPUT(data).then(
                   function(ret){
                       toaster.pop('success', '', '保存成功')
                   },
                   function(ret){
                       district.district_name = originData.district_name;
                       toaster.pop('error', '保存失败', '数据冲突')
                   }
               )
            }
            else {
                // 新建item
                District.post(data).then(function(ret){
                    district.id = ret.id;
                    district.district_name = ret.district_name;
                    toaster.pop('success', '', '保存成功')
                },function(ret){
                        district.id = ret.id;
                        $scope.districts.splice(index, 1);
                        toaster.pop('error', '保存失败', '数据冲突')
                    }
                )
            }

        };

        $scope.removeDistrict = function(index, district){
            if(!district.id){
                $scope.districts.splice(index, 1)
            }
            District.one(district.id).customDELETE().then(function(ret){
                $scope.districts.splice(index, 1);
                toaster.pop('success', '', '删除成功');
            },function(ret){
                toaster.pop('error', '', '删除失败,有其他数据引用此数据')
            })
        };

        $scope.addDistrict = function(){
            $scope.inserted = {
              district_name: null
            };
            $scope.districts.push($scope.inserted);
        };

}]);
}();
