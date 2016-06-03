/**
 * Created by qitian on 2016/5/9 0009.
 */
UserApp.controller('GroupCtrl', ['$scope', '$location','FileUploader', 'Group', 'UserInfo','toaster', function($scope, $location, FileUploader, Group, UserInfo, toaster) {
    UserInfo.one('ss').customGET().then(function(ret){
           $scope.userInfo = ret;
        });

    Group.getList().then(function(ret){
       $scope.groups = ret;
    });

    $scope.groupSelected = null;
    $scope.selectGroup = function(item){
        if(item.selected === false || item.selected === undefined){
            item.selected = true;
            if ($scope.groupSelected !== null){
                $scope.groupSelected.selected = false;
            }
            $scope.groupSelected = item
        }
    };


    var uploader = $scope.uploader = new FileUploader({
        //url: 'http://183.230.40.230:9090/api/group/publish'
        url: 'http://localhost:5000/api/group/publish'
    });
    uploader.filters.push({
            name: 'customFilter',
            fn: function(item /*{File|FileLikeObject}*/, options) {
                return this.queue.length < 1;

            }
        });
    uploader.filters.push({
       name: 'sizeFilter',
        fn: function(item, options){
            return item.size < 1024 * 30;
        }
    });
    uploader.filters.push({
        name: 'fileTypeFilter',
        fn: function(item, option){
            var type = item.name.slice(item.name.lastIndexOf('.') + 1);
            return '|TXT|'.indexOf(type) !== -1;
        }
    });

    $scope.publishAD = function(){
        if($scope.groupSelected == null){
            toaster.pop('error', '未选择要发送的分组')
        }else{
            $scope.uploading = true;
            var item = $scope.uploader.queue[0];

            item.formData = [{'group_id': $scope.groupSelected.group_id, 'user_id': $scope.userInfo.id}];
            $scope.uploader.uploadItem(item);
            $scope.uploader.onCompleteItem = function(item, respone, status, headers){
                $scope.progress_code = respone.progress_code;
                if($scope.progress_code){
                     $scope.timer = $interval(getProgess, 4000, 1000);
                }
            };
        }

    };

    // CALLBACKS

    uploader.onWhenAddingFileFailed = function(item /*{File|FileLikeObject}*/, filter, options) {
        console.info('onWhenAddingFileFailed', item, filter, options);
    };
    uploader.onAfterAddingFile = function(fileItem) {
        console.info('onAfterAddingFile', fileItem);
    };
    uploader.onAfterAddingAll = function(addedFileItems) {
        console.info('onAfterAddingAll', addedFileItems);
    };
    uploader.onBeforeUploadItem = function(item) {
        console.info('onBeforeUploadItem', item);
    };
    uploader.onProgressItem = function(fileItem, progress) {
        console.info('onProgressItem', fileItem, progress);
    };
    uploader.onProgressAll = function(progress) {
        console.info('onProgressAll', progress);
    };
    uploader.onSuccessItem = function(fileItem, response, status, headers) {
        console.info('onSuccessItem', fileItem, response, status, headers);
    };
    uploader.onErrorItem = function(fileItem, response, status, headers) {
        console.info('onErrorItem', fileItem, response, status, headers);
    };
    uploader.onCancelItem = function(fileItem, response, status, headers) {
        console.info('onCancelItem', fileItem, response, status, headers);
    };
    uploader.onCompleteItem = function(fileItem, response, status, headers) {
        console.info('onCompleteItem', fileItem, response, status, headers);
    };
    uploader.onCompleteAll = function() {
        console.info('onCompleteAll');
    };

    console.info('uploader', uploader);

}]);