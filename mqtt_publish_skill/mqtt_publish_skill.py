"""Contains the skill flow_fnished_skill."""
import grpc

from absl import logging

from intrinsic.skills.proto import footprint_pb2
from intrinsic.skills.python import proto_utils
from intrinsic.skills.python import skill_interface
from intrinsic.util.decorators import overrides

from intrinsic.util.grpc import connection
from intrinsic.util.grpc import interceptor

from mqtt_service import mqtt_service_pb2_grpc
from mqtt_service import mqtt_service_pb2

from mqtt_publish_skill import mqtt_publish_skill_pb2

def make_grpc_stub(resource_handle):
    logging.info(f"Address: {resource_handle.connection_info.grpc.address}")
    logging.info(f"Server Instance: {resource_handle.connection_info.grpc.server_instance}")
    logging.info(f"Header: {resource_handle.connection_info.grpc.header}")

    # Create a gRPC channel without using TLS
    grpc_info = resource_handle.connection_info.grpc
    grpc_channel = grpc.insecure_channel(grpc_info.address)
    connection_params = connection.ConnectionParams(
        grpc_info.address, grpc_info.server_instance, grpc_info.header
    )

    intercepted_channel = grpc.intercept_channel(
        grpc_channel,
        interceptor.HeaderAdderInterceptor(connection_params.headers),
    )
    return mqtt_service_pb2_grpc.MqttServiceStub(
        intercepted_channel
    )

class FlowFnishedSkill(skill_interface.Skill):
    """Implementation of the flow_fnished_skill skill."""

    def __init__(self) -> None:
        pass

    @overrides(skill_interface.Skill)
    def get_footprint(
        self,
        request: skill_interface.GetFootprintRequest[mqtt_publish_skill_pb2.MqttPublishSkillParams],
        context: skill_interface.GetFootprintContext,
    ) -> footprint_pb2.Footprint:
        """Returns the resources required for running this skill.

        Skill developers should override this method with their implementation.

        If a skill does not implement `get_footprint`, the default implementation
        specifies that the skill needs exclusive access to everything. The skill
        will therefore not be able to execute in parallel with any other skill.

        Args:
            request: The get footprint request.
            context: Provides access to the world and other services that a skill may
                use.

        Returns:
            The skill's footprint.
        """
        del request  # Unused in this default implementation.
        del context  # Unused in this default implementation.
        return footprint_pb2.Footprint(lock_the_universe=True)

    @overrides(skill_interface.Skill)
    def preview(
        self,
        request: skill_interface.PreviewRequest[mqtt_publish_skill_pb2.MqttPublishSkillParams],
        context: skill_interface.PreviewContext
    ) -> None:
        """Previews the expected outcome of executing the skill.

        `preview` enables an application developer to perform a "dry run" of skill
        execution (or execution of a process that includes that skill) in order to
        preview the effect of executing the skill/process, but without any
        real-world side-effects that normal execution would entail.

        Skill developers should override this method with their implementation. The
        implementation will not have access to hardware resources that are provided
        to `execute`, but will have access to a hypothetical world in which to
        preview the execution. The implementation should return the expected output
        of executing the skill in that world.

        If a skill does not override the default implementation, any process that
        includes that skill will not be executable in "preview" mode.

        NOTE: In preview mode, the object world provided by the PreviewContext
        is treated as the -actual- state of the physical world, rather than as the
        belief state that it represents during normal skill execution. Because of
        this difference, a skill in preview mode cannot introduce or correct
        discrepancies between the physical and belief world (since they are
        identical). For example, if a perception skill only updates the belief state
        when it is executed, then its implementation of `preview` would necessarily
        be a no-op.

        If executing the skill is expected to affect the physical world, then the
        implementation should record the timing of its expected effects using
        `context.record_world_update`. It should NOT make changes to the object
        world via interaction with `context.object_world`.

        The .skill_interface_utils module provides convenience utils that can be
        used to implement `preview` in common scenarios. E.g.:
        - `preview_via_execute`: If executing the skill does not require resources
        or modify the world.

        Args:
            request: The preview request.
            context: Provides access to services that the skill may use.

        Returns:
            The skill's expected result message, or None if it does not return a
            result.

        Raises:
          InvalidSkillParametersError: If the arguments provided to skill parameters
            are invalid.
          SkillCancelledError: If the skill preview is aborted due to a cancellation
            request.
        """
        del request  # Unused in this default implementation.
        del context  # Unused in this default implementation.
        raise NotImplementedError(
            f'Skill "{type(self).__name__!r} has not implemented `preview`.'
        )

    @overrides(skill_interface.Skill)
    def execute(
        self,
        request: skill_interface.ExecuteRequest[mqtt_publish_skill_pb2.MqttPublishSkillParams],
        context: skill_interface.ExecuteContext
    ) -> None:
        logging.info(
            'sending message'
        )
        grpc_stub = make_grpc_stub(context.resource_handles["mqtt_service"])
        mqtt_request = mqtt_service_pb2.mqtt_message()
        mqtt_request.topic = request.params.topic
        mqtt_request.message = request.params.message
        mqtt_request.retained = request.params.retained
        grpc_stub.PublishMessage(mqtt_request)
        return None
