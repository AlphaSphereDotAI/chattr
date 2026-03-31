{ pkgs, lib, config, ... }:
{
  files = {
    ".yamllint.yaml".yaml = {
      extends = "default";
      rules = {
        document-start = "disable";
        truthy = "disable";
        comments = "disable";
        line-length.max = 140;
      };
    };
    ".ruff.toml".toml = {
      target-version = "py314";
      line-length = 120;
      lint = {
        fixable = [ "ALL" ];
        ignore = [ "D100" "D105" "D107" "D212" "D413" "SIM117" ];
        select = [ "ALL" ];
        isort = { combine-as-imports = true; };
        per-file-ignores = {
          "test_app.py" = [ "INP001" "S101" ];
          "__init__.py" = [ "D104" ];
        };
      };
      format = {
        docstring-code-format = false;
        docstring-code-line-length = "dynamic";
        indent-style = "space";
        line-ending = "lf";
        quote-style = "double";
        skip-magic-trailing-comma = false;
      };
    };
    ".ls-lint.yml".yaml = {
      ls = {
        ".py" = "snake_case";
        ".yaml" = "snake_case | kebab-case";
        ".yml" = "snake_case | kebab-case";
        ".toml" = "snake_case";
        ".md" = "SCREAMING_SNAKE_CASE";
      };
      ignore = [ ".devenv" ".git" ];
    };
  };

  # https://devenv.sh/basics/
  env = {
    UV_PYTHON_DOWNLOADS = lib.mkDefault "automatic";
    UV_PYTHON_PREFERENCE = lib.mkDefault "managed";
    SARIF_DIR = "../results";
  };

  # https://devenv.sh/packages/
  packages = with pkgs; [
    taplo
    ls-lint
    trufflehog
    yq-go
    semver
    uv
    commitizen
  ];

  # https://devenv.sh/languages/
  languages = {
    nix = {
      enable = true;
      lsp.enable = true;
    };
    python = {
      enable = true;
      # version = "3.14";
      uv = {
        enable = true;
        sync.enable = true;
      };
    };
  };

  # https://devenv.sh/services/
  # services.postgres.enable = true;

  # https://devenv.sh/processes/
  processes = {
    compatibility-check = {
      exec = "${lib.getExe pkgs.uv} sync --frozen --no-install-project";
    };
    start-dev = {
      exec = "${lib.getExe pkgs.uv} run chattr";
      after = [ "devenv:processes:compatibility-check" ];
      watch = {
        paths = [ ./src ];
        extensions = [ "py" ];
        ignore = [ "__pycache__" "*.pyc" ];
      };
    };
  };

  # https://devenv.sh/tasks/
  tasks = {
    "mkdir:results".exec = "mkdir -p ${config.env.SARIF_DIR}";
    "lint:ruff" = {
      exec = "${lib.getExe pkgs.ruff} check --output-format sarif --output-file ${config.env.SARIF_DIR}/ruff.sarif";
      after = [ "mkdir:results" ];
    };
    "lint:uv_lock_check".exec = "${lib.getExe pkgs.uv} lock --check";
    "lint:ls-lint".exec = "${lib.getExe pkgs.ls-lint}";
    "lint:taplo".exec = "${lib.getExe pkgs.taplo} lint --default-schema-catalogs";
    "lint:ty".exec = "${lib.getExe pkgs.ty} check --output-format github";
    "lint:hadolint" = {
      exec = "${lib.getExe pkgs.hadolint} -f sarif ./repo/Dockerfile > ${config.env.SARIF_DIR}/hadolint.sarif";
      after = [ "mkdir:results" ];
    };
  };

  # https://devenv.sh/tests/
  # enterTest = ''
  #   echo "Running tests"
  #   git --version | grep --color=auto "${pkgs.git.version}"
  # '';

  # https://devenv.sh/git-hooks/
  git-hooks.hooks = {
    action-validator.enable = true;
    actionlint.enable = true;
    nixfmt.enable = true;
    check-added-large-files.enable = true;
    check-builtin-literals.enable = true;
    check-case-conflicts.enable = true;
    check-docstring-first.enable = true;
    check-json.enable = true;
    check-merge-conflicts.enable = true;
    check-python.enable = true;
    check-toml.enable = true;
    check-vcs-permalinks.enable = true;
    check-xml.enable = true;
    check-yaml.enable = true;
    comrak.enable = true;
    deadnix.enable = true;
    detect-private-keys.enable = true;
    # lychee.enable = true;
    markdownlint.enable = true;
    mixed-line-endings.enable = true;
    name-tests-test.enable = true;
    yamlfmt.enable = true;
    python-debug-statements.enable = true;
    ripsecrets.enable = true;
    ruff.enable = true;
    ruff-format.enable = true;
    statix.enable = true;
    taplo.enable = true;
    trim-trailing-whitespace.enable = true;
    trufflehog.enable = true;
    uv-check.enable = true;
    uv-lock.enable = true;
    yamllint.enable = true;
    hadolint.enable = true;
    flynt.enable = true;
  };

  treefmt = {
    enable = true;
    config = {
      programs = {
        ruff-format.enable = true;
        ruff-check.enable = true;
        actionlint.enable = true;
        dockfmt.enable = true;
        # dprint = {
        #   enable = true;
        #   settings = {
        #     newLineKind = "lf";
        #   };
        # };
        jsonfmt.enable = true;
        nixf-diagnose.enable = true;
        nixfmt.enable = true;
        deadnix.enable = true;
        oxipng.enable = true;
        statix.enable = true;
        taplo.enable = true;
        xmllint.enable = true;
        yamlfmt.enable = true;
      };
      settings = {
        formatter = {
          taplo-format = {
            command = "${lib.getExe pkgs.taplo}";
            options = [ "format" ];
            includes = [ "*.toml" ];
            excludes = [ ".git/*" ".devenv/*" ];
          };
        };
      };
    };
  };
  # See full reference at https://devenv.sh/reference/options/
}
