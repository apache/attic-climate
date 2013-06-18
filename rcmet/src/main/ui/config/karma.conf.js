basePath = '../';

files = [
  JASMINE,
  JASMINE_ADAPTER,
  'app/lib/jquery/jquery-1.10.1.js',
  'app/lib/jquery/jquery-ui/jquery-ui-1.10.3.min.js',
  'app/lib/bootstrap/bootstrap.js',
  'app/lib/angular/angular.js',
  'app/lib/angular/angular-*.js',
  'test/lib/angular/angular-mocks.js',
  'app/lib/jquery/jquery-ui/datepicker-wrapper/date.js',
  'app/lib/leaflet/leaflet-0.5.js',
  'app/js/app.js',
  'app/js/controllers/*.js',
  'app/js/directives/*.js',
  'app/js/services/*.js',
  'test/unit/**/*.js'
];

autoWatch = true;

browsers = ['Chrome'];

junitReporter = {
  outputFile: 'test_out/unit.xml',
  suite: 'unit'
};
