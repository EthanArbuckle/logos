from logos_executor import LogosExecutor


class TestOrigDirective:
    def test_orig_no_args(self) -> None:
        test_case = """
        %hook SomeClass
        - (void)methodWithNoArgs {
            %orig;
        }
        %end
        """
        logos_output, stderr = LogosExecutor.preprocess_source(test_case)
        assert logos_output is not None
        assert stderr is None
        assert "_logos_orig$_ungrouped$SomeClass$methodWithNoArgs(self, _cmd);" in logos_output

    def test_orig_single_arg(self) -> None:
        test_case = """
        %hook SomeClass
        - (void)methodWithOneArg:(int)arg {
            %orig(42);
        }
        %end
        """
        logos_output, stderr = LogosExecutor.preprocess_source(test_case)
        assert logos_output is not None
        assert stderr is None
        assert "_logos_orig$_ungrouped$SomeClass$methodWithOneArg$(self, _cmd, 42);" in logos_output

    def test_orig_multiple_args(self) -> None:
        test_case = """
        %hook SomeClass
        - (void)methodWithMultipleArgs:(int)arg1 andString:(NSString *)arg2 {
            %orig(42, @"test");
        }
        %end
        """
        logos_output, stderr = LogosExecutor.preprocess_source(test_case)
        assert logos_output is not None
        assert stderr is None
        assert (
            '_logos_orig$_ungrouped$SomeClass$methodWithMultipleArgs$andString$(self, _cmd, 42, @"test");'
            in logos_output
        )

    def test_orig_block_arg(self) -> None:
        test_case = """
        %hook SomeClass
        - (void)methodWithBlock:(void (^)(int))block {
            %orig(^(int x) {
                NSLog(@"Block called with %d", x);
            });
        }
        %end
        """
        logos_output, stderr = LogosExecutor.preprocess_source(test_case)
        assert logos_output is not None
        assert stderr is None
        assert "_logos_orig$_ungrouped$SomeClass$methodWithBlock$(self, _cmd, ^(int x) {" in logos_output
        assert 'NSLog(@"Block called with %d", x);' in logos_output

    def test_orig_in_hookf(self) -> None:
        test_case = """
        %hookf(int, some_c_function, int arg) {
            int result = %orig(arg + 1);
            return result * 2;
        }
        """
        logos_output, stderr = LogosExecutor.preprocess_source(test_case)
        assert logos_output is not None
        assert stderr is None
        assert "int result = _logos_orig$_ungrouped$some_c_function(arg + 1);" in logos_output

    def test_orig_in_ctor(self) -> None:
        test_case = """
        %hook SomeClass
        + (void)initialize {
            %orig;
            NSLog(@"SomeClass initialized");
        }
        %end

        %ctor {
            %init;
        }
        """
        logos_output, stderr = LogosExecutor.preprocess_source(test_case)
        assert logos_output is not None
        assert stderr is None
        assert "_logos_meta_orig$_ungrouped$SomeClass$initialize(self, _cmd);" in logos_output

    def test_orig_with_return_value(self) -> None:
        test_case = """
        %hook SomeClass
        - (int)methodWithReturnValue {
            int origResult = %orig;
            return origResult + 1;
        }
        %end
        """
        logos_output, stderr = LogosExecutor.preprocess_source(test_case)
        assert logos_output is not None
        assert stderr is None
        assert "int origResult = _logos_orig$_ungrouped$SomeClass$methodWithReturnValue(self, _cmd);" in logos_output

    def test_orig_in_grouped_hook(self) -> None:
        test_case = """
        %group TestGroup
        %hook SomeClass
        - (void)groupedMethod {
            %orig;
            NSLog(@"Grouped method called");
        }
        %end
        %end

        %ctor {
            %init(TestGroup);
        }
        """
        logos_output, stderr = LogosExecutor.preprocess_source(test_case)
        assert logos_output is not None
        assert stderr is None
        assert "_logos_orig$TestGroup$SomeClass$groupedMethod(self, _cmd);" in logos_output

    def test_orig_with_complex_block(self) -> None:
        test_case = """
        %hook SomeClass
        - (void)methodWithComplexBlock:(void (^)(NSString *, NSError *))completion {
            %orig(^(NSString *result, NSError *error) {
                if (error) {
                    NSLog(@"Error: %@", error);
                } else {
                    NSLog(@"Result: %@", result);
                }
                completion(result, error);
            });
        }
        %end
        """
        logos_output, stderr = LogosExecutor.preprocess_source(test_case)
        assert logos_output is not None
        assert stderr is None
        assert (
            "_logos_orig$_ungrouped$SomeClass$methodWithComplexBlock$(self, _cmd, ^(NSString *result, NSError *error) {"
            in logos_output
        )
        assert "if (error) {" in logos_output
        assert 'NSLog(@"Error: %@", error);' in logos_output
        assert 'NSLog(@"Result: %@", result);' in logos_output
        assert "completion(result, error);" in logos_output

    def test_orig_in_new_method(self) -> None:
        test_case = """
        %hook SomeClass
        %new
        - (void)newMethod {
            %orig;  // This should generate a warning
        }
        %end
        """
        _, stderr = LogosExecutor.preprocess_source(test_case)
        assert stderr is not None
        assert "warning: %orig in new method -[SomeClass newMethod] will be non-operative." in stderr

    def test_orig_with_variadic_args(self) -> None:
        test_case = """
        %hook NSString
        + (id)stringWithFormat:(NSString *)format, ... {
            va_list args;
            va_start(args, format);
            id result = %orig(format, args);
            va_end(args);
            return result;
        }
        %end
        """
        logos_output, stderr = LogosExecutor.preprocess_source(test_case)
        assert logos_output is not None
        assert stderr is None
        assert "_logos_meta_orig$_ungrouped$NSString$stringWithFormat$(self, _cmd, format, args);" in logos_output

    def test_orig_inside_of_orig_arg(self) -> None:
        test_case = """
        %hook SomeClass
        - (void)someMethodWithCallback:(void (^)(NSString *, NSError *))callback {
            %orig(^(NSString *result, NSError *error) {

                %orig;  // This should raise an error
                if (error) {
                    NSLog(@"Error: %@", error);
                }
                callback(result, error);
            });
        }
        %end
        """
        _, stderr = LogosExecutor.preprocess_source(test_case)
        assert stderr is not None
        assert "Tweak.x:4: error: %orig cannot be referenced in %orig arguments" in stderr
