/**
 * Created by admin on 2016/5/30 0030.
 */
UserApp.controller('CommandCtrl', ['$scope', 'toaster', 'Group', 'Restangular', 'blockUI',
    function($scope, toaster, Group, Restangular, blockUI){
    var commandUI = blockUI.instances.get('commandUI');
    var command = Restangular.service('command');
    Group.one(0).customGET().then(function(res){
        $scope.buses = res.buses_all;
        //$scope.inGroup = res.in_group;
        angular.forEach($scope.buses, function(route){
            angular.forEach(route.buses, function(bus){
                if(bus.in_group === true)
                    $scope.inGroup.push(bus);
            })
        })
    });

    $scope.selected = null;

    $scope.selectBus = function(bus){
        if (bus.selected == undefined || bus.selected == false){
            bus.selected = true;
            if($scope.selected !== null){
                $scope.selected.selected = false;
            }
            $scope.selected = bus;
        }
    };

    $scope.openPower = function(){
        if($scope.selected !== null){
            commandUI.start();
            command.one('openpower').customPOST($scope.selected).then(function(res){
                toaster.pop('success', '打开电源成功');
                commandUI.stop()
            }, function(res){
                toaster.pop('error', '打开电源失败');
                commandUI.stop();
            });
        }else{
            toaster.pop('error', '还没有选中要发送命令的设备');
        }
    };

    $scope.closePower = function(){
        if($scope.selected !== null){
            command.one('closepower').customPOST($scope.selected).then(function(res){
                toaster.pop('success', '关闭电源成功');
            },function(res){
                toaster.pop('error', '关闭电源失败')
            });
            console.log('发送' + $scope.selected.id);
        }else{
            toaster.pop('error', '还没有选中要发送命令的设备');
        }
    };

    $scope.rssiTest = function(){
        if($scope.selected !== null){
            command.one('rssitest').customPOST($scope.selected).then(function(res){
                toaster.pop('success', '发送RSSI测试命令成功');
            },function(res){
                toaster.pop('error', '发送RSSI测试失败')
            });
        }else{
            toaster.pop('error', '还没有选中要发送命令的设备');
        }
    };

    $scope.uploadMessage1 = function(){
        if($scope.selected !== null){
            command.one('uploadmessage').customPOST($scope.selected).then(function(res){
                toaster.pop('success', '成功上传信息1');
            },function(res){
                toaster.pop('error', '上传测试信息1 失败')
            });
        }else{
            toaster.pop('error', '还没有选中要发送命令的设备');
        }
    };

    $scope.uploadMessage2 = function(){
        if($scope.selected !== null){
            command.one('uploadmessage2').customPOST($scope.selected).then(function(res){
                toaster.pop('success', '成功上传测试信息2');
            },function(res){
                toaster.pop('error', '上传测试信息2 失败')
            });
        }else{
            toaster.pop('error', '还没有选中要发送命令的设备');
        }
    };

}]);