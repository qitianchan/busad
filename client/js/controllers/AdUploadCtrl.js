// TODO:使用观察者模式解决筛选的问题
UserApp.controller('AdUploadCtrl', ['$scope','$interval', 'District', 'Route','Bus', 'PublishAD', 'AbortService', 'FileUploader', 'toaster',
    function($scope, $interval, District, Route, Bus, PublishAD, AbortService, FileUploader, toaster) {


        var uploader = $scope.uploader = new FileUploader({
            url: 'http://localhost:5000/api/publish',
            //url: 'http://183.230.40.230:9090/api/publish'
        });
        $scope.progress_code = '';
        // 进度( 0 - 100 )

        $scope.progress = 0;
        $scope.uploading = false;
        $scope.submitDisable = false;
        //筛选过的路线
        $scope.filterRoutes = [];
        // 筛选过的公交
        $scope.filterBuses = [];

        District.getList().then(function(districts) {
            $scope.districts = districts
        });

        // 线路
        Route.getList().then(function(routes){
            $scope.routes = routes;
            angular.forEach($scope.routes, function(route){
                route.selected = false;
            });
            //初始化被筛选的路线
            $scope.filterRoutes = $scope.routes;
        });

        Bus.getList().then(function(buses){
            $scope.buses = buses;

            angular.forEach($scope.buses, function(bus){
                bus.selected = false;
            });
            $scope.filterBuses = $scope.buses;
        });

        //Watch district change, when changed, all routes or buses which selected will be reset unselected
        $scope.$watch('districtSelected', function(newValue, oldValue){
            //筛选的路线置为空值
            $scope.filterRoutes=[];
            angular.forEach($scope.routes, function (route) {
                route.selected = false;
                if(route.district_id == $scope.districtSelected){
                    //填充经过地区筛选的路线
                    $scope.filterRoutes.push(route);
                }
            });
            angular.forEach($scope.buses, function (bus) {
                bus.selected = false;
            });
            $scope.busAll = false;
            $scope.routeAll = false;
        });

        //选中全部经过地区筛选下来的线路
        $scope.$watch('routeAll', function(newValue, oldValue){
            angular.forEach($scope.filterRoutes, function (route) {
                route.selected = newValue;
            });
        }, true);

        $scope.$watch('busAll', function(newValue, oldValue){
            angular.forEach($scope.filterBuses, function (bus) {
                bus.selected = newValue;
            });
        });

        $scope.$watch('filterRoutes', function(newValue, oldValue) {
            //如果选择的路线变化，跟随着的Bus也变化
            $scope.filterBuses = [];
            angular.forEach($scope.filterRoutes, function(route){
                angular.forEach($scope.buses, function(bus){
                    if(route.selected && bus.route_id == route.id){
                        $scope.filterBuses.push(bus)
                    }
                });
            });
        }, true);


        $scope.publishAD = function(){
            $scope.uploading = true;
            item = $scope.uploader.queue[0];
            euis = [];
            angular.forEach($scope.filterBuses, function(bus){
               if(bus.selected){
                   euis.push(bus.eui)
               }
            });

            item.formData = [{'euis': euis}];
            $scope.uploader.uploadItem(item);
            $scope.uploader.onCompleteItem = function(item, respone, status, headers){
                $scope.progress_code = respone.progress_code;
                if($scope.progress_code){
                     $scope.timer = $interval(getProgess, 4000, 1000);
                }
            };
        };
        // 获取进度
        var getProgess = function(){
            PublishAD.progress($scope.progress_code).then(function(ret){
                    $scope.progress = ret['progress'];
                    var error = ret['error'];
                    if($scope.progress == 100){
                        $interval.cancel($scope.timer);
                        $scope.uploading = false;
                        toaster.pop('success', '发送成功', '');
                    } else if($scope.progress == 408){
                         $interval.cancel($scope.timer);
                        $scope.uploading = false;
                        toaster.pop('error', '发送超时', error);
                    }
                }
            );
        };

        $scope.testProgress = function(){
            if($scope.progress >= 100){
                $scope.progress = 0;
            }
            $scope.progress += 10;
        };

        $scope.abortTest = function(){
            AbortService.getList().then(function(ret){
                toaster.pop('info', '', '开始')
            })
        };

        $scope.abortEnd = function(){
            AbortService.put().then(function(ret){
                toaster.pop('info', '', '终止')
            })
        }
}]);