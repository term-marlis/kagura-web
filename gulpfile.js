var gulp = require('gulp');
var babel = require('gulp-babel');
var uglify = require('gulp-uglify');
var stylus = require('gulp-stylus');
var postcss = require('gulp-postcss');
var csso = require('gulp-csso');
var rename = require('gulp-rename');

var browsers = [
  '> 3%'
];

gulp.task('stylus', function () {
  gulp.src('web/static/css/*.styl')
    .pipe(stylus())
    .pipe(postcss([
      require('autoprefixer', {browsers: browsers}),
      require('css-mqpacker')
    ]))
    .pipe(gulp.dest('web/static/css'))
    .pipe(csso())
    .pipe(rename({extname: '.min.css'}))
    .pipe(gulp.dest('web/static/css'))
});

gulp.task('babel', function () {
  gulp.src('web/static/src/**/*.js')
    .pipe(babel({presets: ['es2015']}))
    .pipe(gulp.dest('web/static/js'))
    .pipe(uglify())
    .pipe(rename({extname: '.min.js'}))
    .pipe(gulp.dest('web/static/js'))
});

gulp.task('watch', ['stylus', 'babel'], function () {
  gulp.watch('web/static/css/*.styl', ['stylus']);
  gulp.watch('web/static/src/**/*.js', ['babel']);
});

gulp.task('default', ['stylus', 'babel']);
