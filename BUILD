load("@bazel_gazelle//:def.bzl", "gazelle")

gazelle(name = "gazelle")

load("@rules_python//python:pip.bzl", "compile_pip_requirements")

compile_pip_requirements(
    name = "requirements",
    src = ":requirements.in",
    requirements_txt = ":requirements_lock.txt",
)
