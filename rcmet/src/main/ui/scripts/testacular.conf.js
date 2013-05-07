basePath = '../';

files = [
  JASMINE,
  JASMINE_ADAPTER,
  'app/js/jquery-1.9.1.min.js',
  'app/js/bootstrap.js',
  'app/lib/angular/angular.js',
  'app/lib/angular/angular-*.js',
  'test/lib/angular/angular-mocks.js',
  'app/js/leaflet.js',
  'app/js/**/*.js',
  'test/unit/**/*.js'
];

autoWatch = true;

browsers = ['Chrome'];

junitReporter = {
  outputFile: 'test_out/unit.xml',
  suite: 'unit'
};
