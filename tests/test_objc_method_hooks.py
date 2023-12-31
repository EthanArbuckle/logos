from logos_executor import LogosExecutor


class TestObjcMethodHooks:
    def test_hook_objc_method__ungrouped_internal_generator(self) -> None:
        # Given a source file that specifies the internal generator, uses no groups,
        # and hooks an objective-c method
        test_case = """
        %config(generator=internal)

        %hook SomeClass

        -(void)hookedMethod {}

        %end
        """

        # When the source file is preprocessed
        logos_output, stderr = LogosExecutor.preprocess_source(test_case)

        # Then the preprocessing should complete successfully
        assert logos_output is not None
        assert stderr is None

        # And the produced output should contain the expected values
        expected_items = [
            "method_setImplementation(",
            "static void _logos_method$_ungrouped$SomeClass$hookedMethod(_LOGOS_SELF_TYPE_NORMAL SomeClass* _LOGOS_SELF_CONST __unused self, SEL __unused _cmd)",
            'Class _logos_class$_ungrouped$SomeClass = objc_getClass("SomeClass");',
            "_logos_superclass$_ungrouped$SomeClass = class_getSuperclass(_logos_class$_ungrouped$SomeClass);",
            "_logos_register_hook(_logos_class$_ungrouped$SomeClass, @selector(hookedMethod), (IMP)&_logos_method$_ungrouped$SomeClass$hookedMethod, (IMP *)&_logos_orig$_ungrouped$SomeClass$hookedMethod);",
        ]
        assert all([expected in logos_output for expected in expected_items])

    def test_hook_objc_method__ungrouped_substrate_generator(self) -> None:
        # Given a source file that specifies the substrate generator, uses no groups,
        # and hooks an objective-c method
        test_case = """
        %config(generator=MobileSubstrate)

        %hook SomeClass

        -(void)hookedMethod {}

        %end
        """

        # When the source file is preprocessed
        logos_output, stderr = LogosExecutor.preprocess_source(test_case)

        # Then the preprocessing should complete successfully
        assert logos_output is not None
        assert stderr is None

        # And the produced output should contain the expected values
        expected_items = [
            "#include <substrate.h>",
            "static void _logos_method$_ungrouped$SomeClass$hookedMethod(_LOGOS_SELF_TYPE_NORMAL SomeClass* _LOGOS_SELF_CONST __unused self, SEL __unused _cmd)",
            'Class _logos_class$_ungrouped$SomeClass = objc_getClass("SomeClass");',
            "MSHookMessageEx(_logos_class$_ungrouped$SomeClass, @selector(hookedMethod), (IMP)&_logos_method$_ungrouped$SomeClass$hookedMethod, (IMP*)&_logos_orig$_ungrouped$SomeClass$hookedMethod);",
            "static void (*_logos_orig$_ungrouped$SomeClass$hookedMethod)",
        ]
        assert all([expected in logos_output for expected in expected_items])

    def test_hook_objc_method__grouped_internal_generator(self) -> None:
        # Given a source file that specifies the internal generator, uses a group,
        # and hooks an objective-c method
        test_case = """
        %config(generator=internal)

        %group foobar
        %hook SomeClass

        -(void)hookedMethod {}

        %end
        %end

        %ctor {
            %init(foobar);
        }
        """

        # When the source file is preprocessed
        logos_output, stderr = LogosExecutor.preprocess_source(test_case)

        # Then the preprocessing should complete successfully
        assert logos_output is not None
        assert stderr is None

        # And the produced output should contain the expected values
        expected_items = [
            "static Class _logos_superclass$foobar$SomeClass; static void (*_logos_orig$foobar$SomeClass$hookedMethod)",
            "static void _logos_method$foobar$SomeClass$hookedMethod(_LOGOS_SELF_TYPE_NORMAL SomeClass* _LOGOS_SELF_CONST __unused self, SEL __unused _cmd)",
            'Class _logos_class$foobar$SomeClass = objc_getClass("SomeClass");',
            "_logos_superclass$foobar$SomeClass = class_getSuperclass(_logos_class$foobar$SomeClass);",
            "logos_register_hook(_logos_class$foobar$SomeClass, @selector(hookedMethod), (IMP)&_logos_method$foobar$SomeClass$hookedMethod, (IMP *)&_logos_orig$foobar$SomeClass$hookedMethod);}",
        ]
        assert all([expected in logos_output for expected in expected_items])

    def test_hook_objc_method__grouped_substrate_generator(self) -> None:
        # Given a source file that specifies the substrate generator, uses a group,
        # and hooks an objective-c method
        test_case = """
        %config(generator=MobileSubstrate)

        %group foobar
        %hook SomeClass

        -(void)hookedMethod {}

        %end
        %end

        %ctor {
            %init(foobar);
        }
        """

        # When the source file is preprocessed
        logos_output, stderr = LogosExecutor.preprocess_source(test_case)

        # Then the preprocessing should complete successfully
        assert logos_output is not None
        assert stderr is None

        # And the produced output should contain the expected values
        expected_items = [
            "#include <substrate.h>",
            "static void (*_logos_orig$foobar$SomeClass$hookedMethod)(_LOGOS_SELF_TYPE_NORMAL SomeClass* _LOGOS_SELF_CONST, SEL);",
            "static void _logos_method$foobar$SomeClass$hookedMethod(_LOGOS_SELF_TYPE_NORMAL SomeClass* _LOGOS_SELF_CONST __unused self, SEL __unused _cmd)",
            'Class _logos_class$foobar$SomeClass = objc_getClass("SomeClass");',
            "MSHookMessageEx(_logos_class$foobar$SomeClass, @selector(hookedMethod), (IMP)&_logos_method$foobar$SomeClass$hookedMethod, (IMP*)&_logos_orig$foobar$SomeClass$hookedMethod);",
        ]
        assert all([expected in logos_output for expected in expected_items])
