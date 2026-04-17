{ pkgs, lib, config, ... }:
{
  files = {
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
    ".hadolint.yaml".yaml = {
      trustedRegistries = [
        "docker.io"
        "ghcr.io"
        "cgr.dev"
      ];
      ignored = [ "DL3018" ];
    };
    ".markdownlint.yaml".yaml = {
      "$schema" = "https://raw.githubusercontent.com/DavidAnson/markdownlint/main/schema/markdownlint-config-schema-strict.json";
      line-length = { tables = false; line_length = 120; };
    };
    ".taplo.toml".toml = {
      exclude = [ ".venv/**" ];
      formatting = {
        reorder_arrays = true;
        reorder_inline_tables = true;
        reorder_keys = true;
      };
    };
    ".trivy.yaml".yaml = {
      ignorefile = ".trivyignore.yaml";
    };
    ".trivyignore.yaml".yaml = { misconfigurations = [ "id: AVD-DS-0026" ]; };
    ".yamlfix.toml".toml = {
      comments_min_spaces_from_content = 1;
      explicit_start = false;
      sequence_style = "block_style";
    };
  };

  env = {
    DOPPLER_ENV = 1;
    SARIF_DIR = "${config.git.root}/sarif";
  };

  packages = with pkgs; [
    taplo
    ls-lint
    trufflehog
    yq-go
    semver
    uv
    ty
    commitizen
  ];

  languages = {
    nix = {
      enable = true;
      lsp.enable = true;
    };
    python = {
      enable = true;
      version = "3.14";
      uv = {
        enable = true;
        sync.enable = true;
      };
    };
    rust.enable = true;
  };

  processes = {
    start-dev = {
      exec = "${lib.getExe pkgs.uv} run chattr";
      watch = {
        paths = [ ./src ];
        extensions = [ "py" ];
        ignore = [ "__pycache__" "*.pyc" ];
      };
    };
  };

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
}