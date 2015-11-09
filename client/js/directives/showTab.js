/**
 * Created by qitian on 2015/11/3.
 */
UserApp.directive('showTab', function() {
  return {
            link: function (scope, element, attrs) {
                element.click(function(e) {
                    e.preventDefault();
                    $(element).tab('show');
                });
            }
        };
});
