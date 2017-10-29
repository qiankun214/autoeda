from autoeda_basefuc import autoeda_module_analysis


class autoeda_testbench_generator(autoeda_module_analysis):
    """docstring for autoeda_testbench_generator"""

    def __init__(self):
        super(autoeda_testbench_generator, self).__init__()
        self.dump_fsdb = ["string dump_file;",
                          "initial begin",
                          "\t`ifdef DUMP",
                          "".join(
                              ["\t\tif($value$plusargs(\"FSDB= ",
                               r"%s", "\" ,dump_file))"]),
                          "".join(
                              ["\t\t\t$display(\"dump_file = ",
                               r"%s", "\",dump_file);", ]),
                          "\t\t$fsdbDumpfile(dump_file);",
                          "\t\t$fsdbDumpvars(0, tb_this_module_name);",
                          "\t`endif",
                          "end"]
        self.dump_fsdb = "\n".join(self.dump_fsdb)
        self.dump_vcd = ["`ifdef VCD_ON",
                         "\tinitial begin",
                         "\t\t# <start>;",
                         "\t\t$dumpfile(\"dut.vcd\");",
                         "\t\t$dumpvars(0,tb_this_module_name.dut);",
                         "\t\t# <hold>;",
                         "\t\t$finish;",
                         "\tend",
                         "`endif"]
        self.dump_vcd = "\n".join(self.dump_vcd)

    def __call__(self, source_path, tb_path="./tb.sv", fsdb=False, vcd=False):
        self.bfuc_read_file(source_path)
        self.bfuc_get_module_name()
        self.bfuc_get_ports()
        tb_content = [self._tb_head_gen()]
        tb_content.append(self.tb_param_define())
        tb_content.append(self.tb_value_define(type_def="logic"))
        tb_content.append(self.tb_module_instances())
        if fsdb is True:
            tb_content.append(self.dump_fsdb.replace(
                "this_module_name", self.module_name))
        if vcd is True:
            tb_content.append(self.dump_vcd.replace(
                "this_module_name", self.module_name))
        tb_content.append(self._clock_gen())
        tb_content.append(self._reset_gen())
        tb_content.append(self._init_input())
        tb_content.append("endmodule")
        self.bfuc_write_file(tb_path, "\n\n".join(tb_content))

    def _tb_head_gen(self):
        if self.module_head is None:
            self.bfuc_get_module_name()
        return "\n".join(["//generated by autoeda\n",
                          "module tb_%s();" % self.module_name])

    def tb_param_define(self):
        param_list = []
        self._check_params_exsist()
        for param in self.params_dict:
            param_list.append(
                "parameter %s = %s;" % (param, self.params_dict[param]))
        return "\n".join(param_list)

    def tb_value_define(self, type_def=None):
        self.bfuc_get_ports()
        var_def_list = []
        for port in self.port_list:
            if type_def is None:
                var_def_list.append(
                    "%s %s%s;" % (
                        port["type"], port["width_source"], port["name"]))
            else:
                var_def_list.append(
                    "%s %s%s;" % (
                        type_def, port["width_source"], port["name"]))
        return "\n".join(var_def_list)

    def tb_module_instances(self, modult_info=None, indent=""):
        if modult_info is None:
            module_name, params_dict, port_list = \
                self.module_name, self.params_dict, self.port_list
        else:
            module_name, params_dict, port_list = modult_info
        if len(params_dict) == 0:
            module_content = ["%s%s dut (" % (module_name, indent)]
        else:
            module_content = ["%s%s #(" % (module_name, indent)]
            module_content.append(self.tb_param_instances(
                params_dict, indent=indent + "\t"))
            module_content.append("%s) dut (" % indent)
        module_content.append(self.tb_port_instances(
            port_list, indent="\t" + indent))
        module_content.append("%s);" % indent)
        return "\n".join(module_content)

    def tb_param_instances(self, params_dict=None, indent="\t"):
        if params_dict is None:
            params_dict = self.params_dict
        param_list = []
        for param in params_dict:
            param_list.append("%s.%s(%s)," % (indent, param, param))
        return "\n".join(param_list)[:-1]

    def tb_port_instances(self, port_list=None, indent="\t"):
        if port_list is None:
            port_list = self.port_list
        port_instance_list = []
        for port in port_list:
            port_instance_list.append("%s.%s(%s)," % (
                indent, port["name"], port["name"]))
        return "\n".join(port_instance_list)[:-1]

    def _clock_gen(self):
        return "\n".join([
            "initial begin",
            "\tclk = 0;",
            "\tforever begin",
            "\t\t # <clock> clk = ~clk;",
            "\tend",
            "end"])

    def _reset_gen(self):
        return "\n".join([
            "initial begin",
            "\trst_n = 1'b1;",
            "\t#5 rst_n = 1'b0",
            "\t#10 rst_n = 1'b1;",
            "end"])

    def _init_input(self):
        return "\n".join(["initial begin",
                          self.tb_var_initial(
                              [x for x in self.port_list
                               if x["type"] == "input"
                               and x["name"] != "clk" and
                               x["name"] != "rst_n"], indent="\t"),
                          "end"])

    def tb_var_initial(self, port_list=None, indent=""):
        if port_list is None:
            port_list = self.port_list
        var_init_list = []
        for port in port_list:
            var_init_list.append("%s%s = 'b0;" % (indent, port["name"]))
        return "\n".join(var_init_list)

if __name__ == '__main__':
    test = autoeda_testbench_generator()
    test("./spi_config.v", fsdb=True, vcd=True)
