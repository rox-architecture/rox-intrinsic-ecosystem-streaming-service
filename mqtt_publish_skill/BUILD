load("@ai_intrinsic_sdks//bazel:skills.bzl", "py_skill", "skill_manifest")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_proto_library")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")

proto_library(
    name = "mqtt_publish_skill_proto",
    srcs = ["mqtt_publish_skill.proto"],
)

py_proto_library(
    name = "mqtt_publish_skill_py_pb2",
    deps = [":mqtt_publish_skill_proto"],
)

skill_manifest(
    name = "mqtt_publish_skill_py_manifest",
    src = "mqtt_publish_skill.manifest.textproto",
    deps = [":mqtt_publish_skill_proto"],
)

py_library(
    name = "mqtt_publish_skill_py",
    srcs = ["mqtt_publish_skill.py"],
    srcs_version = "PY3",
    deps = [
        ":mqtt_publish_skill_py_pb2",
        "//mqtt_service:mqtt_service_py_pb2",
        "//mqtt_service:mqtt_service_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/skills/proto:equipment_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/skills/proto:footprint_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/skills/python:proto_utils",
        "@ai_intrinsic_sdks//intrinsic/skills/python:skill_interface",
        "@ai_intrinsic_sdks//intrinsic/util:decorators",
        "@com_google_absl_py//absl/logging",
        "@com_google_protobuf//:protobuf_python",
        "@ai_intrinsic_sdks//intrinsic/util/grpc:connection",
        "@ai_intrinsic_sdks//intrinsic/util/grpc:interceptor",
    ],
)

py_test(
    name = "mqtt_publish_skill_test",
    size = "small",
    srcs = ["mqtt_publish_skill_test.py"],
    main = "mqtt_publish_skill_test.py",
    deps = [
        ":mqtt_publish_skill_py",
    ],
)

py_skill(
    name = "mqtt_publish_skill",
    manifest = ":mqtt_publish_skill_py_manifest",
    deps = [
        ":mqtt_publish_skill_py",
        ":mqtt_publish_skill_py_pb2",
    ],
)

py_binary(
    name = "mqtt_publish_skill_integration_test",
    srcs = ["mqtt_publish_skill_integration_test.py"],
    main = "mqtt_publish_skill_integration_test.py",
    deps = [
        "@ai_intrinsic_sdks//intrinsic/solutions:behavior_tree",
        "@ai_intrinsic_sdks//intrinsic/solutions:deployments",
    ],
)
