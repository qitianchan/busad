/**
 * Created by admin on 2016/5/16 0016.
 */
UserApp.controller('EditGroupCtrl',['$scope', '$routeParams', 'Route', 'Group', 'Restangular' , function($scope, $routeParams, Route, Group, Restangular) {
    $scope.groupId = $routeParams.groupId;
    var path = $scope.groupId;
    $scope.inGroup = [];
    Group.one(path).customGET().then(function(res){
        $scope.buses = res.buses_all;
        //$scope.inGroup = res.in_group;
        angular.forEach($scope.buses, function(route){
            angular.forEach(route.buses, function(bus){
                if(bus.in_group === true)
                    $scope.inGroup.push(bus);
            })
        })
    });

    $scope.removeNode = function(index){
        var bus = $scope.inGroup.splice(index, 1)[0];
        bus.in_group = false;
    };

    $scope.addBus = function(bus){
        if(bus.in_group === false){
            bus.in_group = true;
            $scope.inGroup.push(bus);
        }else {
            bus.in_group = false;
            for(var i=0; i<$scope.inGroup.length; i++){
                if($scope.inGroup[i].bus_id === bus.bus_id){
                    var target = $scope.inGroup.splice(i, 1)[0];
                    target.in_group = false;
                }
            }
        }
    };
    $scope.updateMember = function(){

        Group.one($routeParams.groupId).one('members').customPUT($scope.inGroup).then(function(res){
            console.log(res.message)
        })
    }

}]);