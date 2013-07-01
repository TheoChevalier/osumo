'use strict';

(function() {
  angular.module('osumo').controller('SettingsViewController', ['$scope', 'title', 'AppService', 'L10NService', function($scope, title, AppService, L10NService) {
    $scope.locale = L10NService.defaultLocale;
    $scope.languages = window.LANGUAGES;

    L10NService.reset();
    title(L10NService._('Settings'));

    $scope.save = function() {
      AppService.setDefaultLocale($scope.locale).then(function() {
        $scope.toast({message: L10NService._("Saved."), autoclose: 1500});
      });
    };
  }]);
})();