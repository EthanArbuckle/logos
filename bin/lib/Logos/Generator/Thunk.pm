package Logos::Generator::Thunk;
use strict;

our $AUTOLOAD;

my %subrefCache;

sub AUTOLOAD {
	my $self = shift;
	my $method = $AUTOLOAD;
	return if $method eq "DESTROY";

	$method =~ s/.*:://;
	my $fullyQualified = $self->{PACKAGE}."::".$method;
	my $subref = $subrefCache{$fullyQualified};

	$subref = $self->can($method) if !$subref;
	if (!$subref) {
		warn("Method '$method' does not exist on package ".$self->{PACKAGE});
		return undef;
	}

	unshift @_, $self->{OBJECT} if $self->{OBJECT};
	goto &$subref;
}

sub can {
	my $self = shift;
	my $method = shift;
	my $subref = $self->SUPER::can($method);
	return $subref if $subref;

	$method =~ s/.*:://;
	my $fullyQualified = $self->{PACKAGE}."::".$method;
	return $subrefCache{$fullyQualified} if $subrefCache{$fullyQualified};
	
	my $package_can = $self->{PACKAGE}->can($method);
	if (!$package_can) {
		return undef;
	}

	$subref = sub {unshift @_, $self->{PACKAGE}; goto &$package_can};
	$subrefCache{$fullyQualified} = $subref;

	return $subref;
}

sub DESTROY {
	my $self = shift;
	$self->SUPER::destroy();
}

sub for {
	my $proto = shift;
	my $class = ref($proto) || $proto;
	my $self = {};
	$self->{PACKAGE} = shift;
	$self->{OBJECT} = shift;
	bless($self, $class);
	return $self;
}

1;
