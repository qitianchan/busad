window.UserApp = angular.module('UserApp', ['ngRoute', 'restangular', 'LocalStorageModule', 'SessionCreateCtrl', 'angularFileUpload', 'xeditable', 'toaster'])

.run(function($location, Restangular, AuthService, editableOptions) {
    Restangular.setFullRequestInterceptor(function(element, operation, route, url, headers, params, httpConfig) {
        if (AuthService.isAuthenticated()) {
            headers['Authorization'] = 'Basic ' + btoa(AuthService.getToken());
        }
        return {
            headers: headers
        };
    });

    Restangular.setErrorInterceptor(function(response, deferred, responseHandler) {
        if (response.config.bypassErrorInterceptor) {
            return true;
        } else {
            switch (response.status) {
                case 401:
                    AuthService.logout();
                    $location.path('/sessions/create');
                    break;
                default:
                    //throw new Error('No handler for status code ' + response.status);
                    return true;
            }
            return false;
        }
    });
        // angular-xeditable
        editableOptions.theme = 'bs3';
})

.config(function($routeProvider, RestangularProvider) {

    RestangularProvider.setBaseUrl('http://localhost:5000/api');
    //RestangularProvider.setBaseUrl('http://183.230.40.230:9090/api');

    var partialsDir = 'partials';

    var redirectIfAuthenticated = function(route) {
        return function($location, $q, AuthService) {

            var deferred = $q.defer();

            if (AuthService.isAuthenticated()) {
                deferred.reject();
                $location.path(route);
            } else {
                deferred.resolve()
            }

            return deferred.promise;
        }
    };

    var redirectIfNotAuthenticated = function(route) {
        return function($location, $q, AuthService) {

            var deferred = $q.defer();

            if (! AuthService.isAuthenticated()) {
                deferred.reject()
                $location.path(route);
            } else {
                deferred.resolve()
            }

            return deferred.promise;
        }
    };

    $routeProvider
        .when('/', {
            controller: 'AdUploadCtrl',
            templateUrl: partialsDir + '/home/adupload.html'
        })
        .when('/sessions/create', {
            controller: 'SessionCreateCtrl',
            templateUrl: partialsDir + '/session/create.html',
            resolve: {
                redirectIfAuthenticated: redirectIfAuthenticated('/')
            }
        })
        .when('/sessions/destroy', {
            controller: 'SessionDestroyCtrl',
            templateUrl: partialsDir + '/session/destroy.html'
        })
        .when('/users/create', {
            controller: 'UserCreateCtrl',
            templateUrl: partialsDir + '/user/create.html'
        })
        .when('/route/routes', {
            controller: 'RouteCtrl',
            templateUrl: partialsDir + '/route/routes.html',
            resolve: {
                redirectIfNotAuthenticated: redirectIfNotAuthenticated('/sessions/create')
            }
        })
        .when('/group', {
            controller: 'GroupCtrl',
            templateUrl: partialsDir + '/group/group.html',
            resolve: {
                redirectIfNotAuthenticated: redirectIfNotAuthenticated('/sessions/create')
            }
        });
});