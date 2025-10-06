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
    # MODEL__API_KEY="${GEMINI_API_KEY}";
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
          backoff_seconds = 2;
          max_restarts = 5;
          restart = "on_failure";
        };
        depends_on = {
          qdrant = {
            condition = "process_completed_successfully";
          };
        };
        # environment = [
        #   "ENVVAR_FOR_THIS_PROCESS_ONLY=foobar"
        # ];
      };
    };
    qdrant.exec = "docker run --rm -d -p 6333:6333 -v 'qdrant_storage:/qdrant/storage:z' qdrant/qdrant";
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
