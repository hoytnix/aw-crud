module.exports = (grunt) ->
    grunt.initConfig
        pkg: grunt.file.readJSON("package.json")

        htmlmin:
            options:
                collapseWhitespace: true
                conservativeCollapse: true
                html5: true
                minifyCSS: true
                minifyJS: true
                removeComments: true
            build:
                files: [{
                    expand: true
                    cwd: 'public'
                    src: ['**/*.html']
                    dest: 'public'
                }]

        uglify:
            options:
                mangle: false
                report: 'min'
                preserveComments: 'some'
            build:
                files: [{
                    expand: true
                    cwd: 'public'
                    src: ['**/*.js', '!**/*.min.js']
                    dest: 'public'
                }]

        cssmin:
            options:
                report: 'min'
                roundingPrecision: -1
            build:
                files: [{
                    expand: true
                    cwd: 'public'
                    src: ['**/*.css', '!**/*.min.css']
                    dest: 'public'
                }]

        imagemin:
            options:
                optimizationLevel: 3
            build:
                files: [{
                    expand: true
                    cwd: 'public'
                    src: ['**/*.{png,jpg,jpeg,gif}']
                    dest: 'public'
                }]

        uncss:
            options:
                report: 'min'
            build:
                files: [{
                    nonull: true,
                    src: [
                            'http://0.0.0.0:5000/',
                            'http://0.0.0.0:5000/blog',
                            'http://0.0.0.0:5000/blog/meta/hello-world-/',
                            'http://0.0.0.0:5000/blog/software/youtube-dl/'
                        ]
                    dest: 'public/static/styles/main.css'
                }]

        cacheBust:
            build:
                options:
                    algorithm: 'md5'
                    length: 5

                    createCopies: true
                    deleteOriginals: true

                    baseDir: 'public/'
                    assets: ['static/**/*.{css,js,png,jpg,jpeg,gif}']
                files: [{
                    expand: true,
                    cwd: 'public/',
                    src: ['**/index.html']
                }]

        copy:
            build:
                files: [{
                    expand: true,
                    cwd: '../flask/hoyt/static'
                    src: ['**', '!**/*.css']
                    dest: 'public/static'
                }]

        fontello:
            build:
                options:
                    config: 'fontello.json'
                    fonts: '../flask/hoyt/static/font'
                    styles: '../flask/hoyt/static/fontello'
                    scss: false
                    force: true

    # Minification / compression.
    grunt.loadNpmTasks "grunt-contrib-uglify"
    grunt.loadNpmTasks "grunt-contrib-cssmin"
    grunt.loadNpmTasks "grunt-contrib-htmlmin"
    grunt.loadNpmTasks "grunt-contrib-imagemin"
    # ...
    grunt.loadNpmTasks "grunt-uncss"
    grunt.loadNpmTasks "grunt-cache-bust"
    grunt.loadNpmTasks "grunt-fontello"
    # Utilities
    grunt.loadNpmTasks "grunt-contrib-copy"
    grunt.loadNpmTasks "grunt-contrib-watch"
    grunt.loadNpmTasks "grunt-newer"

    grunt.registerTask "default", [
        # First collect CSS
        "uncss"
        "cssmin"

        # Then copy over assets and minify them
        "copy"
        "uglify"
        "newer:imagemin:build"

        # Finally hash assets and minify the HTML
        "cacheBust"
        "htmlmin"
    ]
