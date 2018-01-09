from autoeda_template import autoeda_component_template_generator
import json


class autoeda_iopad_package(autoeda_component_template_generator):
    """docstring for autoeda_iopad_package"""

    def __init__(self):
        super(autoeda_iopad_package, self).__init__()

    def __call__(self, top_path, input_pad_path, output_pad_path,
                 pad_config_path, new_top_path="./new_top.v",
                 new_io_path="./io.v"):
        pad_config = self.io_read_config(pad_config_path)
        input_info = self.io_get_pad_info(input_pad_path)
        output_info = self.io_get_pad_info(output_pad_path)
        self.io_get_pad_info(top_path)
        io_content = self.io_generate_package(
            input_info, output_info, pad_config)
        self.bfuc_write_file(new_io_path, io_content)

    def io_get_pad_info(self, path):
        self.__init__()
        self.bfuc_read_file(path)
        self.bfuc_get_module_name()
        self.bfuc_get_ports()
        return self.module_name, self.params_dict, self.port_list

    def io_read_config(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def io_generate_package(self, input_info, output_info, pad_config):
        content = [self._gen_pkg_head(pad_config)]
        for port_info in self.port_list:
            content.append(self._gen_io_instances(
                port_info, input_info, output_info))
        content.append("endmodule")
        return "/n".join(content)

    def _gen_pkg_head(self, pad_config):
        content = []
        for port_info in self.port_list:
            content.append("\n\t%s %s io_%s" % (
                self._io_port_type_gen(port_info["type"], pad_config),
                self._io_port_width_gen(port_info["width_source"]),
                port_info["name"]))
            content.append("\t%s %s %s" % (
                self._port_type_gen(port_info["type"]),
                self._io_port_width_gen(port_info["width_source"]),
                port_info["name"]))
        body_content = ",\n".join(content)
        return "\n".join(["module io_pad (", body_content, ");"])

    def _io_port_type_gen(self, port_type, config):
        if "inout" in config["type"]:
            return "inout"
        else:
            return port_type

    def _port_type_gen(self, port_type):
        if "input" in port_type["type"]:
            return "output"
        else:
            return "input"

    def _io_port_width_gen(self, port_width_source):
        return port_width_source

    def _gen_io_instances(self, port_info, input_info, output_info):
        if "input" in port_info["type"]:
            info = input_info
        else:
            info = output_info
        content = []
        for i in range(port_info["width"]):
            content.append(self.tp_module_instances(
                info,
                instance_name="io_%s_name",
                port_connection_mode=self._io_connection(port_info["name"], i))
            )
        return "\n".join(content)

    def _io_connection(self, info, num):
        def _connection(self, name):
            if info["connect"][name] == "pad":
                return "io_%s[%s]" % (name, num)
            elif info["connect"][name] == "port":
                return "%s[%s]" % (name, num)
            else:
                return info["connect"][name]
        return _connection
