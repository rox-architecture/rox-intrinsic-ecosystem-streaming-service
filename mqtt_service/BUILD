load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@io_bazel_rules_go//proto:def.bzl", "go_proto_library")
load("@io_bazel_rules_go//go:def.bzl", "go_binary")
load("@rules_oci//oci:defs.bzl", "oci_image", "oci_load")
load("@rules_pkg//:pkg.bzl", "pkg_tar")
load("@ai_intrinsic_sdks//intrinsic/assets/services/build_defs:services.bzl", "intrinsic_service")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_grpc_library", "py_proto_library")

proto_library(
    name = "mqtt_service_proto",
    srcs = ["mqtt_service.proto"],
)

go_proto_library(
    name = "mqtt_service_go_pb2",
    compilers = ["@io_bazel_rules_go//proto:go_grpc"],
    importpath = "eu.sotec/mqtt_service_proto",
    protos = [
       ":mqtt_service_proto",
    ],
    visibility = ["//visibility:public"],
)

py_proto_library(
    name = "mqtt_service_py_pb2",
    deps = [":mqtt_service_proto"],
    visibility = ["//visibility:public"],
)

py_grpc_library(
    name = "mqtt_service_py_pb2_grpc",
    srcs = [":mqtt_service_proto"],
    grpc_library = "@pypi_deps//grpcio:pkg",
    deps = [":mqtt_service_py_pb2"],
    visibility = ["//visibility:public"],
)

go_binary(
    name = "server",
    srcs = ["server.go"],
    data = [],
    deps = [
        ":mqtt_service_go_pb2",

        "@io_bazel_rules_go//go/runfiles",
        "@org_golang_google_grpc//credentials/insecure",
        "@org_golang_google_grpc//:go_default_library",
        "@org_golang_google_grpc//metadata",
        "@ai_intrinsic_sdks//intrinsic/resources/proto:runtime_context_go_proto",
        "@ai_intrinsic_sdks//intrinsic/util/proto:protoio",

        "@com_github_eclipse_paho_mqtt_golang//:go_default_library",
    ]
)

pkg_tar(
    name = "server_layer",
    srcs = [":server"],
    extension = "tar.gz",
    include_runfiles = True,
)

oci_image(
    name = "mqtt_service_image",
    base = "@distroless_base",
    entrypoint = ["/server"],
    tars = [":server_layer"],
)

oci_load(
    name = "mqtt_service_tarball",
    image = ":mqtt_service_image",
    repo_tags = ["mqtt_service:latest"],
)

filegroup(
    name = "mqtt_service_tarball.tar",
    srcs = [":mqtt_service_tarball"],
    output_group = "tarball",
)

intrinsic_service(
    name = "mqtt_service",
    images = [":mqtt_service_tarball.tar"],
    manifest = "mqtt_service_manifest.textproto",
    deps = [":mqtt_service_proto"],
    default_config = "mqtt_service_default_config.textproto"
)
