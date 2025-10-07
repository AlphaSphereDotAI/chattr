{ pkgs
, lib
, config
, inputs
, ...
}:

{
  name = "chattr";
  dotenv.enable = true;
  # https://devenv.sh/basics/
  env = {
    GREET = "devenv";
    MODEL__URL = "https://generativelanguage.googleapis.com/v1beta/openai/";
    # MODEL__API_KEY = builtins.getEnv "GEMINI_API_KEY";
    MODEL__NAME = "gemini-2.5-flash-lite";
  };

  # https://devenv.sh/packages/
  packages = [ pkgs.git ];

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    uv = {
      enable = true;
      sync = {
        enable = true;
      };
    };
  };

  # https://devenv.sh/processes/
  # processes.dev.exec = "${lib.getExe pkgs.watchexec} -n -- ls -la";
  processes = {
    chattr = {
      exec = "${lib.getExe pkgs.uv} run chattr";
      process-compose = {
        availability = {
          max_restarts = 5;
          restart = "on_failure";
        };
        depends_on = {
          qdrant = {
            condition = "process_healthy";
          };
          vocalizr = {
            condition = "process_healthy";
          };
          visualizr = {
            condition = "process_healthy";
          };
        };
        readiness_probe = {
          http_get = {
            host = "127.0.0.1";
            scheme = "http";
            path = "/";
            port = 7860;
          };
        };
      };
    };
    qdrant = {
      exec = ''
        docker run --rm --name qdrant \
        -p 6333:6333 \
        -v 'qdrant_storage:/qdrant/storage:z' \
        qdrant/qdrant
      '';
      process-compose = {
        availability = {
          max_restarts = 5;
          restart = "on_failure";
        };
        launch_timeout_seconds = 60;
        readiness_probe = {
          http_get = {
            host = "127.0.0.1";
            scheme = "http";
            path = "/";
            port = 6333;
          };
        };
        shutdown.command = "docker stop qdrant";
      };
    };
    vocalizr = {
      exec = ''
        docker run --rm --name vocalizr \
        -p 7861:7860 \
        -v 'huggingface:/home/nonroot/hf' \
        -v 'results:/home/nonroot/results' \
        -v 'logs:/home/nonroot/logs' \
        --user root \
        alphaspheredotai/vocalizr
      '';
      process-compose = {
        availability = {
          max_restarts = 10;
          restart = "on_failure";
        };
        launch_timeout_seconds = 60;
        readiness_probe = {
          http_get = {
            host = "127.0.0.1";
            scheme = "http";
            path = "/";
            port = 7861;
          };
          initial_delay_seconds = 100;
        };
        shutdown.command = "docker stop vocalizr";
      };
    };
    visualizr = {
      exec = ''
        docker run --rm --name visualizr \
        -p 7862:7860 \
        -v 'checkpoint:/home/nonroot/ckpts' \
        -v 'gfpgan:/home/nonroot/gfpgan' \
        -v 'results:/home/nonroot/results' \
        -v 'assets:/home/nonroot/assets' \
        -v 'logs:/home/nonroot/logs' \
        --user root \
        alphaspheredotai/visualizr
      '';
      process-compose = {
        availability = {
          max_restarts = 10;
          restart = "on_failure";
        };
        launch_timeout_seconds = 60;
        readiness_probe = {
          http_get = {
            host = "127.0.0.1";
            scheme = "http";
            path = "/";
            port = 7862;
          };
          initial_delay_seconds = 100;
        };
        shutdown.command = "docker stop visualizr";
      };
    };
  };

  # https://devenv.sh/services/
  # services.postgres.enable = true;

  # https://devenv.sh/scripts/
  # scripts = {
  #   # hello.exec = ''
  #   #   echo hello from $GREET
  #   # '';
  #   chattr.exec = "${lib.getExe pkgs.uv} run chattr";
  # };

  # https://devenv.sh/basics/
  enterShell = ''
    # hello         # Run scripts directly
    git --version # Use packages
  '';

  # https://devenv.sh/tasks/
  # tasks = {
  #   "chattr:run" = {
  #     exec = "${lib.getExe pkgs.uv} run chattr";
  #     # execIfModified = [ "src" ];
  #     after = [ "qdrant:start" ];
  #   };
  #   "qdrant:start" = {
  #     exec = "docker run --rm -p 6333:6333 -v 'qdrant_storage:/qdrant/storage:z' qdrant/qdrant";
  #     before = [ "devenv:processes:chattr" ];
  #   };
  #   # "devenv:enterShell".after = [ "myproj:setup" ];
  # };

  # https://devenv.sh/tests/
  enterTest = ''
    echo "Running tests"
    git --version | grep --color=auto "${pkgs.git.version}"
  '';

  # https://devenv.sh/git-hooks/
  # git-hooks.hooks.shellcheck.enable = true;

  # See full reference at https://devenv.sh/reference/options/
}
