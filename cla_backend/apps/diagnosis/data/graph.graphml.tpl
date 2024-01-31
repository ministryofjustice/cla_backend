{% load i18n %}<?xml version='1.0' encoding='UTF-8' standalone='no'?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:java="http://www.yworks.com/xml/yfiles-common/1.0/java" xmlns:sys="http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0" xmlns:x="http://www.yworks.com/xml/yfiles-common/markup/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:yed="http://www.yworks.com/xml/yed/3" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">
  <!--Created by yEd 3.23.2-->
  <key for="port" id="d0" yfiles.type="portgraphics"/>
  <key for="port" id="d1" yfiles.type="portgeometry"/>
  <key for="port" id="d2" yfiles.type="portuserdata"/>
  <key attr.name="body" attr.type="string" for="node" id="d3"/>
  <key attr.name="title" attr.type="string" for="node" id="d4"/>
  <key attr.name="context:test" attr.type="string" for="node" id="d5">
    <default xml:space="preserve"/>
  </key>
  <key attr.name="context:xml" for="node" id="d6">
    <default/>
  </key>
  <key attr.name="order" attr.type="int" for="node" id="d7">
    <default xml:space="preserve">9999</default>
  </key>
  <key attr.name="help" attr.type="string" for="node" id="d8">
    <default xml:space="preserve"/>
  </key>
  <key attr.name="heading" attr.type="string" for="node" id="d9">
    <default xml:space="preserve"/>
  </key>
  <key attr.name="permanent_id" attr.type="string" for="node" id="d10"/>
  <key attr.name="url" attr.type="string" for="node" id="d11"/>
  <key attr.name="description" attr.type="string" for="node" id="d12"/>
  <key for="node" id="d13" yfiles.type="nodegraphics"/>
  <key for="graphml" id="d14" yfiles.type="resources"/>
  <key attr.name="url" attr.type="string" for="edge" id="d15"/>
  <key attr.name="description" attr.type="string" for="edge" id="d16"/>
  <key for="edge" id="d17" yfiles.type="edgegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="n0">
      <data key="d3" xml:space="preserve">{% trans "Education" %}</data>
      <data key="d4" xml:space="preserve">Education</data>
      <data key="d7" xml:space="preserve">4</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}The education category of law covers all issues arising out of education including:

* Special Educational Needs (SEN)
* learning difficulties
* discrimination in the provision of education
* admissions
* exclusions
* bullying
* children being out of school

Please note education covers nursery education, primary, secondary and higher education as well as home schooling, training and apprenticeships.{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n0</data>
      </node>
    <node id="n1">
      <data key="d3" xml:space="preserve">{% trans "Diagnosis for operators" %}</data>
      <data key="d4" xml:space="preserve">Diagnosis for operators</data>
      <data key="d5" xml:space="preserve">testcontext</data>
      <data key="d10" xml:space="preserve">start</data>
      </node>
    <node id="n2">
      <data key="d3" xml:space="preserve">{% trans "Debt and housing - loss of home" %}</data>
      <data key="d4" xml:space="preserve">Debt/Housing - Loss of Home</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}This category covers the legal area of Debt, and the areas of Housing covering home loss.

Debt covers advice on

* struggling to manage/pay debt
* council tax, housing or mortgage arrears
* dealing with creditors, loan sharks and illegal money lenders
* Debt Relief Orders, Individual Voluntary Arrangements (IVA), Bankruptcy and Administration
* dealing with bailiffs and charges placed on perperty in lieu of unpaid debt
* being in receipt of a claim from the court
* being subject to non-conformity of creditors from previous agreements
* dealing with payment of court fines

Housing covers advice on

* homelessness
* notices for eviction
* illegal eviction or possession
* notices for possession
* rent arrears
* UKBA issues

The following are covered in 'other housing'.

* threatened loss of home or harassment from landlords
* disrepair / poor housing conditions
* ASBO/ASBI

Clients in temporary accommodation will be covered for in scope housing.{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n2</data>
      </node>
    <node id="n3">
      <data key="d3" xml:space="preserve">{% trans "Home owner, and the nature of the debt means they are at immediate risk of losing their home (Includes shared ownership if the client is living in the property)" %}</data>
      <data key="d4" xml:space="preserve">Client owns a house </data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}A client's home is defined as the house, caravan, houseboat or other vehicle or structure that is their only or main residence. The references to caravan, houseboat or other vehicle include the land on which it is located or to which it is moored.

Operators should interpret the definition as a client would only be in scope if they lived in the home in question. If someone lives or owns another property and the matter relates to a different proeperty to the one they live in then this would be out of scope.

If the client is a co-owner of the property and they live in it as their only or main residence (as per the definition of 'home') then this would be in scope.

Search guidance for 'timeline' to see the home repossession timeline.

*FYI: Debt matters need to arise from an issue where the client owns their own home. Problems relating to homes that are rented or leased from another person fall within Housing.*{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n3</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n4">
      <data key="d3" xml:space="preserve">{% trans "The mortgage lender is seeking or has sought a court order to recover the property (due to mortgage arrears)" %}</data>
      <data key="d4" xml:space="preserve">Mortgage lender is s</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}Check the mortgage possession timeline in guidance - search for 'timeline'.

Record here how you have identified that the mortgage lender is seeking/has sought a court order enabling them to recover possession of the client's property.

Record in Operator Notes what documents client has received. These may include a Default Notice or Possession Warrant.{% endblocktrans %}</data>
      <data key="d9" xml:space="preserve">{% trans "Select the type of documentation the client has received:" %}</data>
      <data key="d10" xml:space="preserve">n4</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n5">
      <data key="d3" xml:space="preserve">{% trans "A warrant of possession has been received by client" %}</data>
      <data key="d4" xml:space="preserve">Client has received </data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d9" xml:space="preserve">{% trans "HEADING ON WARRANT" %}</data>
      <data key="d10" xml:space="preserve">n5</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n6">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">debt</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n6</data>
      </node>
    <node id="n7">
      <data key="d3" xml:space="preserve">{% trans "A claim form has been received by client" %}</data>
      <data key="d4" xml:space="preserve">Client has received </data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d9" xml:space="preserve">{% trans "HEADING ON CLAIM FORM" %}</data>
      <data key="d10" xml:space="preserve">n7</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n8">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">debt</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n8</data>
      </node>
    <node id="n9">
      <data key="d3" xml:space="preserve">{% trans "The client has other documentation that places their home at immediate (date-based) risk" %}</data>
      <data key="d4" xml:space="preserve">Other documentation </data>
      <data key="d7" xml:space="preserve">4</data>
      <data key="d9" xml:space="preserve">{% trans "HEADING ON OTHER" %}</data>
      <data key="d10" xml:space="preserve">n9</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n10">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">debt</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n10</data>
      </node>
    <node id="n11">
      <data key="d3" xml:space="preserve">{% trans "A creditor is seeking a court order forcing the sale of the client’s property to recoup the debt they are owed" %}</data>
      <data key="d4" xml:space="preserve">Creditor is seeking </data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d9" xml:space="preserve">{% trans "Select the type of documentation the client has received:" %}</data>
      <data key="d10" xml:space="preserve">n11</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n12">
      <data key="d3" xml:space="preserve">{% trans "Sale of client's home is being forced in order to recoup a charging order on their property." %}</data>
      <data key="d4" xml:space="preserve">Client has received </data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}A Charging Order is placed on a property by the court securing an outstanding debt against the home or other property.

This alone will not constitute a serious risk to the client's home, but if there is a court order forcing the sale of the home in order to recoup the debt then this will be in scope.

If a client disagrees with a charging order that is in place, and wants to know how to set it aside, or requires general advice regarding the order, then this will be out of scope unless a court is forcing them to sell their home to recoup the debt.

If client has received a charging order please record this in Operator Notes.{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n12</data>
      </node>
    <node id="n13">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">debt</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n13</data>
      </node>
    <node id="n14">
      <data key="d3" xml:space="preserve">{% trans "Letter Before Action received by client" %}</data>
      <data key="d4" xml:space="preserve">Client has received </data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d8" xml:space="preserve">{% trans "client is being taken to court on a given date due to debt" %}</data>
      <data key="d10" xml:space="preserve">n14</data>
      </node>
    <node id="n15">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">debt</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n15</data>
      </node>
    <node id="n16">
      <data key="d3" xml:space="preserve">{% trans "Other documentation that places client’s own home at immediate (date based) risk." %}</data>
      <data key="d4" xml:space="preserve">Other documentation </data>
      <data key="d10" xml:space="preserve">n16</data>
      </node>
    <node id="n17">
      <data key="d3" xml:space="preserve">{% trans "A creditor is seeking to make the client bankrupt in order to recoup the debt they are owed and the client’s estate includes their own home" %}</data>
      <data key="d4" xml:space="preserve">Creditor is seeking </data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d9" xml:space="preserve">{% trans "Select the type of documentation the client has received:" %}</data>
      <data key="d10" xml:space="preserve">n17</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n18">
      <data key="d3" xml:space="preserve">{% trans "Statutory Demand" %}</data>
      <data key="d4" xml:space="preserve">Client has received </data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d8" xml:space="preserve">{% trans "court has ordered the client sell their house" %}</data>
      <data key="d10" xml:space="preserve">n18</data>
      </node>
    <node id="n19">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">debt</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n19</data>
      </node>
    <node id="n20">
      <data key="d3" xml:space="preserve">{% trans "Bankruptcy Petition" %}</data>
      <data key="d4" xml:space="preserve">Client has received </data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d8" xml:space="preserve">{% trans "formal notification that third party wants to make client bankrupt through the courts" %}</data>
      <data key="d10" xml:space="preserve">n20</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n21">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">debt</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n21</data>
      </node>
    <node id="n22">
      <data key="d3" xml:space="preserve">{% trans "Other documentation that places client’s own home at immediate (date based) risk." %}</data>
      <data key="d4" xml:space="preserve">Other documentation </data>
      <data key="d10" xml:space="preserve">n22</data>
      </node>
    <node id="n23">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">debt</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n23</data>
      </node>
    <node id="n24">
      <data key="d3" xml:space="preserve">{% trans "In rented accommodation" %}</data>
      <data key="d4" xml:space="preserve">client in rented acc</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n24</data>
      </node>
    <node id="n25">
      <data key="d3" xml:space="preserve">{% trans "The landlord is seeking to recover possession of the property" %}</data>
      <data key="d4" xml:space="preserve">Landlord is seeking </data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d9" xml:space="preserve">{% trans "Select the type of documentation the client has received:" %}</data>
      <data key="d10" xml:space="preserve">n25</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n26">
      <data key="d3" xml:space="preserve">{% trans "Letter from the landlord confirming that informal arrangements can no longer continue" %}</data>
      <data key="d4" xml:space="preserve">Client has received </data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n26</data>
      </node>
    <node id="n27">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n27</data>
      </node>
    <node id="n28">
      <data key="d3" xml:space="preserve">{% trans "Notice to Quit (a letter from the landlord giving the tenant notice to leave the property - for cases where the renting arrangement does not have a secure tenure)" %}</data>
      <data key="d4" xml:space="preserve">Client has received </data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n28</data>
      </node>
    <node id="n29">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n29</data>
      </node>
    <node id="n30">
      <data key="d3" xml:space="preserve">{% trans "Letter Before Action (a letter the landlord sends before starting proceedings to recover possession of the property)" %}</data>
      <data key="d4" xml:space="preserve">Client has received </data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d10" xml:space="preserve">n30</data>
      </node>
    <node id="n31">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n31</data>
      </node>
    <node id="n32">
      <data key="d3" xml:space="preserve">{% trans "Notices from the landlord under section 83 of the Housing Act 1985 and sections 8 and 21 of the Housing Act 1988 (these give the client notice before the landlord starts formal possession proceedings for the property)" %}</data>
      <data key="d4" xml:space="preserve">Client has received </data>
      <data key="d7" xml:space="preserve">4</data>
      <data key="d10" xml:space="preserve">n32</data>
      </node>
    <node id="n33">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n33</data>
      </node>
    <node id="n34">
      <data key="d3" xml:space="preserve">{% trans "Possession proceedings - issued by the court and giving the client notice of a hearing date for possession proceedings" %}</data>
      <data key="d4" xml:space="preserve">Possession proceedin</data>
      <data key="d7" xml:space="preserve">8</data>
      <data key="d10" xml:space="preserve">n34</data>
      </node>
    <node id="n35">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n35</data>
      </node>
    <node id="n36">
      <data key="d3" xml:space="preserve">{% trans "Possession Order from the court (this gives the client notice of possession - at the end of the specified period the creditor may apply to bailiffs to execute a warrant for possession)" %}</data>
      <data key="d4" xml:space="preserve">The client has recei</data>
      <data key="d7" xml:space="preserve">5</data>
      <data key="d10" xml:space="preserve">n36</data>
      </node>
    <node id="n37">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n37</data>
      </node>
    <node id="n38">
      <data key="d3" xml:space="preserve">{% trans "Warrant for eviction from the court bailiffs (this gives county court bailiffs the power to evict occupiers and change the locks)" %}</data>
      <data key="d4" xml:space="preserve">The client has recei</data>
      <data key="d7" xml:space="preserve">6</data>
      <data key="d10" xml:space="preserve">n38</data>
      </node>
    <node id="n39">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n39</data>
      </node>
    <node id="n40">
      <data key="d3" xml:space="preserve">{% trans "There is other evidence that landlord is seeking to recover possession and placing the home at immediate risk" %}</data>
      <data key="d4" xml:space="preserve">There is other evide</data>
      <data key="d7" xml:space="preserve">7</data>
      <data key="d10" xml:space="preserve">n40</data>
      </node>
    <node id="n41">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n41</data>
      </node>
    <node id="n42">
      <data key="d3" xml:space="preserve">{% trans "None of the above - consider whether discrimination might apply" %}</data>
      <data key="d4" xml:space="preserve">If none of the above</data>
      <data key="d10" xml:space="preserve">n42</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n43">
      <data key="d3" xml:space="preserve">{% trans "The landlord is unlawfully evicting the client without due process (eg will be changing the locks)" %}</data>
      <data key="d4" xml:space="preserve">Landlord is unlawful</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n43</data>
      </node>
    <node id="n44">
      <data key="d3" xml:space="preserve">{% trans "Describe scenario carefully in notes - client's circumstances and why they believe they are facing eviction or have been evicted. *Then click 'next' to continue*" %}</data>
      <data key="d4" xml:space="preserve">Describe scenario ca</data>
      <data key="d10" xml:space="preserve">n44</data>
      </node>
    <node id="n45">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n45</data>
      </node>
    <node id="n46">
      <data key="d3" xml:space="preserve">{% trans "Homeless or at risk of becoming homeless within 56 days" %}</data>
      <data key="d4" xml:space="preserve">Client becoming homeless</data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d9" xml:space="preserve">{% trans "Select the option that best describes the client’s situation." %}</data>
      <data key="d10" xml:space="preserve">n46</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n47">
      <data key="d3" xml:space="preserve">{% trans "The landlord has unlawfully evicted the client without due process" %}</data>
      <data key="d4" xml:space="preserve">Landlord has unlawfu</data>
      <data key="d8" xml:space="preserve">{% trans "(eg changed the locks)" %}</data>
      <data key="d10" xml:space="preserve">n47</data>
      </node>
    <node id="n48">
      <data key="d3" xml:space="preserve">{% trans "Describe scenario carefully in notes - including the client's circumstances and why they believe they are facing eviction or have been evicted" %}</data>
      <data key="d4" xml:space="preserve">Describe scenario ca</data>
      <data key="d10" xml:space="preserve">n48</data>
      </node>
    <node id="n49">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n49</data>
      </node>
    <node id="n50">
      <data key="d3" xml:space="preserve">{% trans "An informal licensing or renting arrangement is ending" %}</data>
      <data key="d4" xml:space="preserve">Informal licensing/r</data>
      <data key="d10" xml:space="preserve">n50</data>
      </node>
    <node id="n51">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n51</data>
      </node>
    <node id="n52">
      <data key="d3" xml:space="preserve">{% trans "The client has received a Notice to Quit from the landlord" %}</data>
      <data key="d4" xml:space="preserve">Notice to Quit from </data>
      <data key="d10" xml:space="preserve">n52</data>
      </node>
    <node id="n53">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n53</data>
      </node>
    <node id="n54">
      <data key="d3" xml:space="preserve">{% trans "The client can't access their home (eg due to letter from partner, closure order for property)" %}</data>
      <data key="d4" xml:space="preserve">Client unable to acc</data>
      <data key="d10" xml:space="preserve">n54</data>
      </node>
    <node id="n55">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n55</data>
      </node>
    <node id="n56">
      <data key="d3" xml:space="preserve">{% trans "A court has issued possession proceedings" %}</data>
      <data key="d4" xml:space="preserve">Possession proceedin</data>
      <data key="d10" xml:space="preserve">n56</data>
      </node>
    <node id="n57">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n57</data>
      </node>
    <node id="n58">
      <data key="d3" xml:space="preserve">{% trans "The client has received a possession order from the court (outlining the decision of the court)" %}</data>
      <data key="d4" xml:space="preserve">Client received a po</data>
      <data key="d10" xml:space="preserve">n58</data>
      </node>
    <node id="n59">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n59</data>
      </node>
    <node id="n60">
      <data key="d3" xml:space="preserve">{% trans "The client has received a warrant for eviction from the court bailliffs" %}</data>
      <data key="d4" xml:space="preserve">Client received a wa</data>
      <data key="d10" xml:space="preserve">n60</data>
      </node>
    <node id="n61">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n61</data>
      </node>
    <node id="n62">
      <data key="d3" xml:space="preserve">{% trans "The client has received a letter from the local authority saying that they do not qualify for accommodation or assistance and they want to challenge this decision" %}</data>
      <data key="d4" xml:space="preserve">Client received a le</data>
      <data key="d10" xml:space="preserve">n62</data>
      </node>
    <node id="n63">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n63</data>
      </node>
    <node id="n64">
      <data key="d3" xml:space="preserve">{% trans "The client believes it is not reasonable to continue to occupy the property (eg a recently disabled person can't easily access the property, the client can't afford to live in the property, there is a threat of violence towards the client or their family)" %}</data>
      <data key="d4" xml:space="preserve">Client believes that</data>
      <data key="d10" xml:space="preserve">n64</data>
      </node>
    <node id="n65">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n65</data>
      </node>
    <node id="n66">
      <data key="d3" xml:space="preserve">{% trans "The client is being refused accommodation or has had it terminated by the UK Border Force" %}</data>
      <data key="d4" xml:space="preserve">Client is being refu</data>
      <data key="d10" xml:space="preserve">n66</data>
      </node>
    <node id="n67">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n67</data>
      </node>
    <node id="n68">
      <data key="d3" xml:space="preserve">{% trans "Other (please give details in notes)" %}</data>
      <data key="d4" xml:space="preserve">Other</data>
      <data key="d7" xml:space="preserve">99999</data>
      <data key="d10" xml:space="preserve">n68</data>
      </node>
    <node id="n69">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n69</data>
      </node>
    <node id="n70">
      <data key="d3" xml:space="preserve">{% trans "Owes other money (check that the consequences of this don’t place the client in another category of debt)" %}</data>
      <data key="d4" xml:space="preserve">Other money owed (ch</data>
      <data key="d7" xml:space="preserve">4</data>
      <data key="d10" xml:space="preserve">n70</data>
      </node>
    <node id="n71">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve"> 	<category xml:space="preserve">debt</category> </context>
      </data>
      <data key="d10" xml:space="preserve">n71</data>
      </node>
    <node id="n72">
      <data key="d3" xml:space="preserve">{% trans "None of the above -  consider whether discrimination might apply and click on 'Help' for examples" %}</data>
      <data key="d4" xml:space="preserve">If none of the above</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}Examples of discrimination in the debt and housing category might include:

* the client has been treated differently by their landlord compared to other tenants of the same landlord
* the landlord has refused to make reasonable adjustments to the property to accommodate a client's disability
* an estate agent is only offering a minority group properties that are considered hard to let{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n72</data>
      </node>
    <node id="n73">
      <data key="d3" xml:space="preserve">{% trans "Other housing matters" %}</data>
      <data key="d4" xml:space="preserve">Other housing matter</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}This category covers the legal area of Housing outside home loss.

It covers advice on

* threatened loss of home or harassment from landlords
* disrepair / poor housing conditions - only where rented accomodation.
* ASBO/ASBI

For loss of home please click 'back' and select the first category.{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n73</data>
      </node>
    <node id="n74">
      <data key="d3" xml:space="preserve">{% trans "Housing disrepair (necessary repairs have not been carried out) - for people in **rented** accomodation only" %}</data>
      <data key="d4" xml:space="preserve">Housing disrepair is</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d9" xml:space="preserve">{% trans "Select the option that best describes the client’s situation." %}</data>
      <data key="d10" xml:space="preserve">n74</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n75">
      <data key="d3" xml:space="preserve">{% trans "Client has photos of disrepair AND the disrepair puts them or their family at serious risk of harm or injury (this includes an injury or illness that has already happened)" %}</data>
      <data key="d4" xml:space="preserve">Client has photos of</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n75</data>
      </node>
    <node id="n76">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n76</data>
      </node>
    <node id="n77">
      <data key="d3" xml:space="preserve">{% trans "Client has report by an expert (e.g. a surveyor) on the disrepair AND the disrepair puts them or their family at serious risk of harm, injury or illness" %}</data>
      <data key="d4" xml:space="preserve">Client has report by</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n77</data>
      </node>
    <node id="n78">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n78</data>
      </node>
    <node id="n79">
      <data key="d3" xml:space="preserve">{% trans "ASBO/ASBI (Antisocial Behaviour Order/Antisocial Behaviour Injunction)" %}</data>
      <data key="d4" xml:space="preserve">ASBO/ASBI</data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d10" xml:space="preserve">n79</data>
      </node>
    <node id="n80">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n86</data>
      </node>
    <node id="n81">
      <data key="d3" xml:space="preserve">{% trans "Harassment (being threatened or disturbed in your home, on more than one occasion)" %}</data>
      <data key="d4" xml:space="preserve">Harrassment (being d</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n89</data>
      </node>
    <node id="n82">
      <data key="d3" xml:space="preserve">{% trans "Client is being harassed by a landlord and needs injunction or restraining order" %}</data>
      <data key="d4" xml:space="preserve">Client is being hara</data>
      <data key="d10" xml:space="preserve">n90</data>
      </node>
    <node id="n83">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n91</data>
      </node>
    <node id="n84">
      <data key="d3" xml:space="preserve">{% trans "Client is being harassed by a neighbour and needs injunction or restraining order" %}</data>
      <data key="d4" xml:space="preserve">Client is being hara</data>
      <data key="d10" xml:space="preserve">n92</data>
      </node>
    <node id="n85">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n93</data>
      </node>
    <node id="n86">
      <data key="d3" xml:space="preserve">{% trans "Other out of scope, rediagnose" %}</data>
      <data key="d4" xml:space="preserve">Other out of</data>
      <data key="d10" xml:space="preserve">n94</data>
      </node>
    <node id="n87">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n95</data>
      </node>
    <node id="n88">
      <data key="d3" xml:space="preserve">{% trans "None of the above" %}</data>
      <data key="d4" xml:space="preserve">None of the above</data>
      <data key="d10" xml:space="preserve">n96</data>
      </node>
    <node id="n89">
      <data key="d3" xml:space="preserve">{% trans "Family" %}</data>
      <data key="d4" xml:space="preserve">Family</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
<subheading xml:space="preserve">If a local authority is involved in taking a child into care and the applicant has received a letter of proceedings or letter of issue sent or client has a court date, a financial assessment is not required</subheading>
</context>
      </data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}The family category of law includes advice on:

* difficulty in getting contact with children or being denied contact
* trying to get custody and parental rights
* Social Services involvement with a child
* protection from domestic abuse (including psychological, physical, financial, sexual or emotional abuse)
* rights and entitlements in divorce or separation
* appointing a guardian and the rights of a guardian
* trying to adopt a child who's in care
* enforcing previous court orders
* child abduction{% endblocktrans %}</data>
      <data key="d9" xml:space="preserve">{% trans "If a child is being taken into care, a financial assessment may not be required." %}</data>
      <data key="d10" xml:space="preserve">n97</data>
      </node>
    <node id="n90">
      <data key="d3" xml:space="preserve">{% trans "Domestic abuse (including child abuse) - the client wants to protect themselves or their children" %}</data>
      <data key="d4" xml:space="preserve">Client protecting self</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}DV/CA - Where a Client wants to seek a court order to protect themselves or a child from abuse via a court order (an injunction) that tells a person they're not allowed to do a certain act. There are two main forms of injunction

A non-molestation order - aimed at preventing a client's partner or ex-partner from using or threatening violence against them or their child, or intimidating, harassing or pestering them.

An occupation order can restrict who can live in the family home, and even restrict the abuser from entering the surrounding area. They can also be used where clients do not feel safe continuing to live with their partner, or if they have already left home because of abuse, but want to return and exclude the abuser.{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n98</data>
      </node>
    <node id="n91">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">family</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n99</data>
      </node>
    <node id="n92">
      <data key="d3" xml:space="preserve">{% trans "Child abduction - the client wants advice" %}</data>
      <data key="d4" xml:space="preserve"/>
      <data key="d7" xml:space="preserve">5</data>
      <data key="d10" xml:space="preserve">n100</data>
      </node>
    <node id="n93">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">family</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n101</data>
      </node>
    <node id="n94">
      <data key="d3" xml:space="preserve">{% trans "Care or adoption proceedings by a local authority (public law)" %}</data>
      <data key="d4" xml:space="preserve">Public law
</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d8" xml:space="preserve">{% trans "Typically the local council is involved due to child protection concerns." %}</data>
      <data key="d9" xml:space="preserve">{% trans "Are they the parent of the child or someone with parental responsibility?" %}</data>
      <data key="d10" xml:space="preserve">n102</data>
      </node>
    <node id="n95">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">family</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n103</data>
      </node>
    <node id="n96">
      <data key="d3" xml:space="preserve">{% trans "None of the above (including guardianship, wills and probate, power of attorney, finding a family mediator)" %}</data>
      <data key="d4" xml:space="preserve">None of the above (i</data>
      <data key="d7" xml:space="preserve">4</data>
      <data key="d10" xml:space="preserve">n104</data>
      </node>
    <node id="n97">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">family</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n105</data>
      </node>
    <node id="n98">
      <data key="d3" xml:space="preserve">{% trans "Discrimination" %}</data>
      <data key="d4" xml:space="preserve">Discrimination</data>
      <data key="d7" xml:space="preserve">5</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}The discrimination category covers advice on cases that contravene the Equalities Act 2010.

It is against the law to discriminate against anyone because of:

* age
* gender reassignment
* being married or in a civil partnership
* being pregnant or having recently given birth
* disability
* race including colour, nationality, ethnic or national origin
* religion, belief or lack of religion or belief
* sex
* sexual orientation

These are called 'protected characteristics'. To find out more, search the guidance for 'protected characteristics'.

The client's problem could start in another category (eg housing) but the client will believe that thay have been discriminated against, harassed or victimised.{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n106</data>
      </node>
    <node id="n99">
      <data key="d3" xml:space="preserve">{% blocktrans %}The client has been discriminated against, or they've been treated badly because they complained about discrimination or supported someone else’s discrimination claim

It is against the law to discriminate against anyone because of:

* age
* gender reassignment
* being married or in a civil partnership
* being pregnant or having recently given birth
* disability
* race including colour, nationality, ethnic or national origin
* religion, belief or lack of religion or belief
* sex
* sexual orientation{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">Has the client been </data>
      <data key="d9" xml:space="preserve">{% trans "Select the type of discrimination that applies" %}</data>
      <data key="d10" xml:space="preserve">n107</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n100">
      <data key="d3" xml:space="preserve">{% trans "Direct discrimination" %}</data>
      <data key="d4" xml:space="preserve">Direct discriminatio</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d8" xml:space="preserve">{% trans "Direct discrimination means being treated less favourably than someone else in similar circumstances due to a protected characteristic (eg the client thinks that they've been singled out for worse treatment or disadvantaged in some way compared to someone else). This includes situations where clients are linked to a person with a protected characteristic and suffer less favourable treatment as a result." %}</data>
      <data key="d9" xml:space="preserve">{% blocktrans %}On what basis has the client been discriminated against?
Give details in the operator notes, especially if more than one option applies.{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n108</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n101">
      <data key="d3" xml:space="preserve">{% trans "Disability" %}</data>
      <data key="d4" xml:space="preserve">Disability Pregnancy</data>
      <data key="d7" xml:space="preserve">5</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}Disability is defined as a physical or mental impairment, which has a substantial and long term adverse effect on a person's ability to carry out normal day-to-day activities.

People with cancer or who are HIV+ are classed as having a disability.

The disability does not have to have a name or a diagnosis to meet this definition.{% endblocktrans %}</data>
      <data key="d9" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">n109</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n102">
      <data key="d3" xml:space="preserve">{% trans "Work" %}</data>
      <data key="d4" xml:space="preserve">Work</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n110</data>
      </node>
    <node id="n103">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">DISCRIMINATION INSCO</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n111</data>
      </node>
    <node id="n104">
      <data key="d3" xml:space="preserve">{% trans "Provision of a service (eg a meal in a restaurant, access to a shopping mall)" %}</data>
      <data key="d4" xml:space="preserve">Provision of a servi</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n112</data>
      </node>
    <node id="n105">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">DISCRIMINATION INSCO</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n113</data>
      </node>
    <node id="n106">
      <data key="d3" xml:space="preserve">{% trans "Exercise of a public function (eg a police officer carrying out a search as part of a criminal investigation)" %}</data>
      <data key="d4" xml:space="preserve">Exercise of a public</data>
      <data key="d7" xml:space="preserve">4</data>
      <data key="d10" xml:space="preserve">n114</data>
      </node>
    <node id="n107">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">DISCRIMINATION INSCO</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n115</data>
      </node>
    <node id="n108">
      <data key="d3" xml:space="preserve">{% trans "Association or private club (eg a golf club, a private members' club)" %}</data>
      <data key="d4" xml:space="preserve">Association or priva</data>
      <data key="d7" xml:space="preserve">5</data>
      <data key="d10" xml:space="preserve">n116</data>
      </node>
    <node id="n109">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">DISCRIMINATION INSCO</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n117</data>
      </node>
    <node id="n110">
      <data key="d3" xml:space="preserve">{% trans "At home (in rental accommodation)" %}</data>
      <data key="d4" xml:space="preserve">Premises</data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d10" xml:space="preserve">n118</data>
      </node>
    <node id="n111">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">DISCRIMINATION INSCO</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n119</data>
      </node>
    <node id="n112">
      <data key="d3" xml:space="preserve">{% trans "Education (schools)" %}</data>
      <data key="d4" xml:space="preserve">Education (schools)</data>
      <data key="d7" xml:space="preserve">6</data>
      <data key="d10" xml:space="preserve">n120</data>
      </node>
    <node id="n113">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">DISCRIMINATION INSCO</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n121</data>
      </node>
    <node id="n114">
      <data key="d3" xml:space="preserve">{% trans "Education (higher education or general qualification bodies)" %}</data>
      <data key="d4" xml:space="preserve">Education (higher ed</data>
      <data key="d7" xml:space="preserve">7</data>
      <data key="d10" xml:space="preserve">n122</data>
      </node>
    <node id="n115">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">DISCRIMINATION INSCO</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n123</data>
      </node>
    <node id="n116">
      <data key="d3" xml:space="preserve">{% trans "Age (the client is under 18)" %}</data>
      <data key="d4" xml:space="preserve">Age (where client is</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}This refers to discrimination against people of a:
* particular age (eg 17-year-olds), or
* range of ages (eg 10 to 15-year-olds){% endblocktrans %}</data>
      <data key="d9" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">n124</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n117">
      <data key="d3" xml:space="preserve">{% trans "Work" %}</data>
      <data key="d4" xml:space="preserve">Work</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n125</data>
      </node>
    <node id="n118">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">DISCRIMINATION INSCO</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n126</data>
      </node>
    <node id="n119">
      <data key="d3" xml:space="preserve">{% trans "Association or private club (eg a golf club, a private members' club)" %}</data>
      <data key="d4" xml:space="preserve">Association or priva</data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d10" xml:space="preserve">n127</data>
      </node>
    <node id="n120">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">DISCRIMINATION INSCO</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n128</data>
      </node>
    <node id="n121">
      <data key="d3" xml:space="preserve">{% trans "Education (higher education/general qualification bodies)" %}</data>
      <data key="d4" xml:space="preserve">Education (higher ed</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n129</data>
      </node>
    <node id="n122">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">DISCRIMINATION INSCO</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n130</data>
      </node>
    <node id="n123">
      <data key="d3" xml:space="preserve">{% trans "Other" %}</data>
      <data key="d4" xml:space="preserve">Other</data>
      <data key="d10" xml:space="preserve">n131</data>
      </node>
    <node id="n124">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOF</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n132</data>
      </node>
    <node id="n125">
      <data key="d3" xml:space="preserve">{% trans "Age (the client is 18 or over)" %}</data>
      <data key="d4" xml:space="preserve">Age (where client is</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}This refers to discrimination against people of a:
* particular age (eg 19-year-olds), or
* range of ages (eg 60 to 80-year-olds){% endblocktrans %}</data>
      <data key="d9" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">n133</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n126">
      <data key="d3" xml:space="preserve">{% trans "Work" %}</data>
      <data key="d4" xml:space="preserve">Work</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n134</data>
      </node>
    <node id="n127">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">DISCRIMINATION INSCO</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n135</data>
      </node>
    <node id="n128">
      <data key="d3" xml:space="preserve">{% trans "Provision of a service (eg a meal in a restaurant, access to a shopping mall)" %}</data>
      <data key="d4" xml:space="preserve">Provision of a servi</data>
      <data key="d7" xml:space="preserve">4</data>
      <data key="d10" xml:space="preserve">n136</data>
      </node>
    <node id="n129">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">DISCRIMINATION INSCO</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n137</data>
      </node>
    <node id="n130">
      <data key="d3" xml:space="preserve">{% trans "Exercise of a public function (eg a police officer carrying out a search)" %}</data>
      <data key="d4" xml:space="preserve">Exercise of a public</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n138</data>
      </node>
    <node id="n131">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">DISCRIMINATION INSCO</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n139</data>
      </node>
    <node id="n132">
      <data key="d3" xml:space="preserve">{% trans "Association or private club (eg a golf club, a private members' club)" %}</data>
      <data key="d4" xml:space="preserve">Association or priva</data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d10" xml:space="preserve">n140</data>
      </node>
    <node id="n133">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">DISCRIMINATION INSCO</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n141</data>
      </node>
    <node id="n134">
      <data key="d3" xml:space="preserve">{% trans "Education (higher education/general qualification bodies)" %}</data>
      <data key="d4" xml:space="preserve">Education (higher ed</data>
      <data key="d7" xml:space="preserve">5</data>
      <data key="d10" xml:space="preserve">n142</data>
      </node>
    <node id="n135">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">DISCRIMINATION INSCO</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n143</data>
      </node>
    <node id="n136">
      <data key="d3" xml:space="preserve">{% trans "Other" %}</data>
      <data key="d4" xml:space="preserve">Other</data>
      <data key="d10" xml:space="preserve">n144</data>
      </node>
    <node id="n137">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOF</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n145</data>
      </node>
    <node id="n138">
      <data key="d3" xml:space="preserve">{% trans "Being married or in a civil partnership" %}</data>
      <data key="d4" xml:space="preserve">Marriage and civil p</data>
      <data key="d7" xml:space="preserve">6</data>
      <data key="d8" xml:space="preserve">{% trans "This refers to people who are married or in a civil partnership, including same sex couples." %}</data>
      <data key="d9" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">n146</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n139">
      <data key="d3" xml:space="preserve">{% trans "Work" %}</data>
      <data key="d4" xml:space="preserve">Work</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n147</data>
      </node>
    <node id="n140">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">DISCRIMINATION INSCO</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n148</data>
      </node>
    <node id="n141">
      <data key="d3" xml:space="preserve">{% trans "Other" %}</data>
      <data key="d4" xml:space="preserve">Other</data>
      <data key="d10" xml:space="preserve">n149</data>
      </node>
    <node id="n142">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOF</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n150</data>
      </node>
    <node id="n143">
      <data key="d3" xml:space="preserve">{% trans "Indirect discrimination" %}</data>
      <data key="d4" xml:space="preserve">Indirect discriminat</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d8" xml:space="preserve">{% trans "The client thinks that new ways of doing things have put them at a disadvantage compared to someone else because of a protected characteristic (eg an employer states that employees cannot have dreadlocks or a pub refuses access to people with hats. This puts employees or patrons of a certain religion at a disadvantage when compared to others.)" %}</data>
      <data key="d9" xml:space="preserve">{% blocktrans %}On what basis has the client been discriminated against?
Give details in the operator notes, especially if more than one option applies.{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n151</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n144">
      <data key="d3" xml:space="preserve">{% trans "Harassment" %}</data>
      <data key="d4" xml:space="preserve">Harassment - Somethi</data>
      <data key="d7" xml:space="preserve">6</data>
      <data key="d8" xml:space="preserve">{% trans "Something happened to make the client feel that they were in an environment that was intimidating, hostile, degrading, humiliating or offensive or that violated their dignity." %}</data>
      <data key="d9" xml:space="preserve">{% blocktrans %}On what basis has the client been discriminated against?
Give details in the operator notes, especially if more than one option applies.{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n152</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n145">
      <data key="d3" xml:space="preserve">{% trans "Victimisation due to a discrimination claim" %}</data>
      <data key="d4" xml:space="preserve">Victimisation due to</data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d8" xml:space="preserve">{% trans "The client thinks that they have been treated worse, or disadvantaged in some way, because they have brought a claim of discrimination, given evidence or information in relation to someone else’s claim of discrimination, made a complaint of discrimination, or been suspected of doing one of these things. For example, an employee is dismissed after making a discrimination claim." %}</data>
      <data key="d9" xml:space="preserve">{% blocktrans %}On what basis has the client been discriminated against?
Give details in the operator notes, especially if more than one option applies.{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n153</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n146">
      <data key="d3" xml:space="preserve">{% trans "Special educational needs (SEN) in a child or young person under 25 - client could be the parent or the child or young person" %}</data>
      <data key="d4" xml:space="preserve">Client has parental </data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n154</data>
      </node>
    <node id="n147">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n155</data>
      </node>
    <node id="n148">
      <data key="d3" xml:space="preserve">{% trans "Advised to bring judicial review proceedings in an education matter" %}</data>
      <data key="d4" xml:space="preserve">They have been advis</data>
      <data key="d7" xml:space="preserve">4</data>
      <data key="d10" xml:space="preserve">n156</data>
      </node>
    <node id="n149">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n157</data>
      </node>
    <node id="n150">
      <data key="d3" xml:space="preserve">{% trans "Discrimination may have occurred due to the child or young person’s SEN or other protected characteristic (eg a school excludes a disabled child from a school trip, a student is being bullied because they're gay but the school is taking no action)" %}</data>
      <data key="d4" xml:space="preserve">Discrimination may a</data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d8" xml:space="preserve">{% trans "Search guidance for 'discrimination education' for more information and a list of questions to ask." %}</data>
      <data key="d10" xml:space="preserve">n158</data>
      </node>
    <node id="n151">
      <data key="d3" xml:space="preserve">{% trans "The client's problem is about admissions, exclusions, other disciplinary procedures, school trips, bullying, any problems at school caused by a child’s disability or any other similar situation" %}</data>
      <data key="d4" xml:space="preserve">Problem covers admis</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n159</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n152">
      <data key="d3" xml:space="preserve">{% trans "Any other education problem" %}</data>
      <data key="d4" xml:space="preserve">None of the above</data>
      <data key="d10" xml:space="preserve">n160</data>
      </node>
    <node id="n153">
      <data key="d3" xml:space="preserve">{% trans "The client is a teacher or employee of the local authority" %}</data>
      <data key="d4" xml:space="preserve">Teacher or employee </data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n161</data>
      </node>
    <node id="n154">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n162</data>
      </node>
    <node id="n155">
      <data key="d3" xml:space="preserve">{% trans "The client is calling for general advice, not about a legal issue specific to them (eg they want to know if a school can stop them removing their child, as opposed to calling after the school has taken action against them for removing their child)" %}</data>
      <data key="d4" xml:space="preserve">Calling for general </data>
      <data key="d10" xml:space="preserve">n163</data>
      </node>
    <node id="n156">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n164</data>
      </node>
    <node id="n157">
      <data key="d3" xml:space="preserve">{% trans "Welfare benefits" %}</data>
      <data key="d4" xml:space="preserve">Welfare benefits</data>
      <data key="d7" xml:space="preserve">6</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}The welfare benefits category of law covers advice on:

* entitlement to benefits and help when benefits are refused
* benefit appeals and tribunals
* problems with housing, welfare and disability benefits and tax credits
* advice on changes in circumstances that would affect benefits or tax credits

The client's problem will be in scope for legal aid if:

* they want to appeal a benefits decision on a point of law in the Upper Tribunal, Court of Appeal or Supreme Court
* a first-tier tribunal has refused them permission to appeal a benefits decision in the Upper Tribunal, and they want advice about how to appeal this decision

All other benefit problems are out of scope.{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n165</data>
      </node>
    <node id="n158">
      <data key="d3" xml:space="preserve">{% trans "The client wants to appeal their benefits decision on a point of law in the Upper Tribunal, Court of Appeal or Supreme Court. (Or a first-tier tribunal has refused the client permission to appeal their benefits decision in the Upper Tribunal and they want advice about how to appeal this decision.)" %}</data>
      <data key="d4" xml:space="preserve">Primary question: Cl</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n166</data>
      </node>
    <node id="n159">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">benefits</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n167</data>
      </node>
    <node id="n160">
      <data key="d3" xml:space="preserve">{% trans "None of the above" %}</data>
      <data key="d4" xml:space="preserve">None of the above</data>
      <data key="d10" xml:space="preserve">n168</data>
      </node>
    <node id="n161">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">benefits</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n169</data>
      </node>
    <node id="n162">
      <data key="d3" xml:space="preserve">{% trans "Employment" %}</data>
      <data key="d4" xml:space="preserve">Employment</data>
      <data key="d7" xml:space="preserve">7</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}The employment category covers advice on

* redundancies, dismissals and disciplinaries
* contracts, workers' rights and working hours
* rights at work including health &amp; safety and accidents at work
* employment status
* holidays, time off, sick leave, maternity &amp; paternity leave and other absence
* pay, tax and the National Minimum Wage.{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n170</data>
      </node>
    <node id="n163">
      <data key="d3" xml:space="preserve">{% trans "The client may have been discriminated against (eg employer not making reasonable adjustments for a disability)" %}</data>
      <data key="d4" xml:space="preserve">Discrimination may a</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}More examples of discrimination issues include issues around:

* equal pay
* being treated worse due to pregnancy or maternity leave
* sexual harassment in the workplace
* being victimised due to having made a claim of discrimination in the workplace{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n171</data>
      </node>
    <node id="n164">
      <data key="d3" xml:space="preserve">{% trans "Discrimination does not apply (Confirm no other matters such as homelessness arise as a result of employment issue)" %}</data>
      <data key="d4" xml:space="preserve">Discrimination does </data>
      <data key="d10" xml:space="preserve">n172</data>
      </node>
    <node id="n165">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">employment</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n173</data>
      </node>
    <node id="n166">
      <data key="d3" xml:space="preserve">{% trans "Consumer" %}</data>
      <data key="d4" xml:space="preserve">Consumer</data>
      <data key="d7" xml:space="preserve">8</data>
      <data key="d8" xml:space="preserve">{% trans "The key thing to determine in this category is whether the client has been discriminated against. Discrimination cases will be in scope. All other consumer cases will be out of scope." %}</data>
      <data key="d10" xml:space="preserve">n174</data>
      </node>
    <node id="n167">
      <data key="d3" xml:space="preserve">{% trans "The client may have been discriminated against" %}</data>
      <data key="d4" xml:space="preserve">Emp discrimination?</data>
      <data key="d10" xml:space="preserve">n175</data>
      </node>
    <node id="n168">
      <data key="d3" xml:space="preserve">{% trans "Discrimination does not apply" %}</data>
      <data key="d4" xml:space="preserve">out of sco</data>
      <data key="d10" xml:space="preserve">n176</data>
      </node>
    <node id="n169">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE </data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">consumer</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n177</data>
      </node>
    <node id="n170">
      <data key="d3" xml:space="preserve">{% trans "Claims against public authorities" %}</data>
      <data key="d4" xml:space="preserve">Actions against the </data>
      <data key="d7" xml:space="preserve">9</data>
      <data key="d8" xml:space="preserve">{% trans "The key thing to determine in claims against public authorities is whether the client has been discriminated against. If the client says they have been discriminated against, or if you pick up that they have been discriminated against from what they say, select 'The client has been discriminated against' on the next screen to proceed to the discrimination flow." %}</data>
      <data key="d10" xml:space="preserve">n178</data>
      </node>
    <node id="n171">
      <data key="d3" xml:space="preserve">{% trans "The client has been discriminated against (eg a police officer used racially abusive language when making an arrest)" %}</data>
      <data key="d4" xml:space="preserve">Client has been subj</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n179</data>
      </node>
    <node id="n172">
      <data key="d3" xml:space="preserve">{% trans "Discrimination does not apply" %}</data>
      <data key="d4" xml:space="preserve">Client has not been </data>
      <data key="d10" xml:space="preserve">n180</data>
      </node>
    <node id="n173">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE DISCL</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">aap</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n181</data>
      </node>
    <node id="n174">
      <data key="d3" xml:space="preserve">{% trans "Crime" %}</data>
      <data key="d4" xml:space="preserve">Crime</data>
      <data key="d7" xml:space="preserve">10</data>
      <data key="d10" xml:space="preserve">n182</data>
      </node>
    <node id="n175">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE DISCLAIME</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">crime</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n183</data>
      </node>
    <node id="n176">
      <data key="d3" xml:space="preserve">{% trans "Clinical negligence" %}</data>
      <data key="d4" xml:space="preserve">Clinical Negligence</data>
      <data key="d7" xml:space="preserve">12</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}Signpost clinical negligence cases to face-to-face providers in the client's area.
Generally, only cases that relate to infants with a brain injury are in scope for legal aid but it's possible that other cases may qualify for exceptional case funding.{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n184</data>
      </node>
    <node id="n177">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">clinneg</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n185</data>
      </node>
    <node id="n178">
      <data key="d3" xml:space="preserve">{% trans "Immigration and asylum" %}</data>
      <data key="d4" xml:space="preserve">Immigration and Asyl</data>
      <data key="d7" xml:space="preserve">11</data>
      <data key="d10" xml:space="preserve">n186</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n179">
      <data key="d3" xml:space="preserve">{% trans "Any other matter" %}</data>
      <data key="d4" xml:space="preserve">Client not subject t</data>
      <data key="d10" xml:space="preserve">n187</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n180">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE DISCLAIME</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">immigration</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n189</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n181">
      <data key="d3" xml:space="preserve">{% trans "The client is losing their home due to the Border Force refusing to support them or withdrawing their support" %}</data>
      <data key="d4" xml:space="preserve">Client is losing hom</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n421</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n182">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">N422</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n183">
      <data key="d3" xml:space="preserve">{% trans "Mental health" %}</data>
      <data key="d4" xml:space="preserve">Mental Health</data>
      <data key="d7" xml:space="preserve">13</data>
      <data key="d10" xml:space="preserve">n191</data>
      </node>
    <node id="n184">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE D</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">mentalhealth</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n192</data>
      </node>
    <node id="n185">
      <data key="d3" xml:space="preserve">{% trans "Personal injury" %}</data>
      <data key="d4" xml:space="preserve">Personal Injury</data>
      <data key="d7" xml:space="preserve">14</data>
      <data key="d8" xml:space="preserve">{% trans "The key thing to determine in this category is whether the client has been discriminated against. Discrimination cases will be in scope. All other personal injury cases will be out of scope." %}</data>
      <data key="d10" xml:space="preserve">n193</data>
      </node>
    <node id="n186">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE DISCLA</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">pi</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n194</data>
      </node>
    <node id="n187">
      <data key="d3" xml:space="preserve">{% trans "The client has been discriminated against" %}</data>
      <data key="d4" xml:space="preserve"/>
      <data key="d5" xml:space="preserve">Discrimination applies
</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n195</data>
      <data key="d12" xml:space="preserve">The client has been discriminated against
</data>
      </node>
    <node id="n188">
      <data key="d3" xml:space="preserve">{% trans "Discrimination does not apply" %}</data>
      <data key="d4" xml:space="preserve"/>
      <data key="d10" xml:space="preserve">n196</data>
      </node>
    <node id="n189">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve"/>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n197</data>
      <data key="d12" xml:space="preserve">OUTOFSCOPE</data>
      </node>
    <node id="n190">
      <data key="d3" xml:space="preserve">{% trans "The client has been discriminated against" %}</data>
      <data key="d4" xml:space="preserve">If none of the above</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n198</data>
      </node>
    <node id="n191">
      <data key="d3" xml:space="preserve">{% trans "Discrimination does not apply" %}</data>
      <data key="d4" xml:space="preserve">No discrimination</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n199</data>
      </node>
    <node id="n192">
      <data key="d3" xml:space="preserve">{% trans "Client in rented accomodation" %}</data>
      <data key="d4" xml:space="preserve">Rented property</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n200</data>
      </node>
    <node id="n193">
      <data key="d3" xml:space="preserve">{% trans "Client is homeowner" %}</data>
      <data key="d4" xml:space="preserve">Client is homeowner</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n201</data>
      </node>
    <node id="n194">
      <data key="d3" xml:space="preserve">{% trans "None of the above apply" %}</data>
      <data key="d4" xml:space="preserve">None of above
</data>
      <data key="d7" xml:space="preserve">4</data>
      <data key="d10" xml:space="preserve">n202</data>
      </node>
    <node id="n195">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">debt</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n203</data>
      </node>
    <node id="n196">
      <data key="d3" xml:space="preserve">{% trans "Client does not have BOTH evidence of the disrepair AND reason to believe the disrepair poses a serious risk of harm, injury or illness to them or their family" %}</data>
      <data key="d4" xml:space="preserve">Not both</data>
      <data key="d10" xml:space="preserve">n204</data>
      </node>
    <node id="n197">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n205</data>
      </node>
    <node id="n198">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">debt</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n206</data>
      </node>
    <node id="n199">
      <data key="d3" xml:space="preserve">{% trans "Client is the alleged abusive partner and wants to defend an injunction. This will be in scope for Civil Legal Advice." %}</data>
      <data key="d4" xml:space="preserve">Client wants to contest injunction DV</data>
      <data key="d7" xml:space="preserve">4</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}Where a Client wants to seek a court order to protect themselves or a child from abuse via a court order 'an injunction' that tells a person they're not allowed to do a certain act. There are two main forms of injunction

* A non-molestation order - aimed at preventing your partner or ex-partner from using or threatening violence against you or your child, or intimidating, harassing or pestering you, in order to ensure the health, safety and well-being of yourself and your children.

* An occupation order can aimed at deciding who can live in the family home, and can also restrict your abuser from entering the surrounding area. If you do not feel safe continuing to live with your partner, or if you have left home because of violence, but want to return and exclude your abuser, you may want to apply for an occupation order.

Some clients who are the alleged abuser do not agree with the injunction against them and wish to get help in defending themselves against it.{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n207</data>
      </node>
    <node id="n200">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">family</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n208</data>
      </node>
    <node id="n201">
      <data key="d3" xml:space="preserve">{% trans "The client is being harassed by a partner, ex-partner or family member" %}</data>
      <data key="d4" xml:space="preserve">Client being harassed by partner or ex-partner</data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d8" xml:space="preserve">{% trans "Seeking protection from a partner, ex partner or other family member due to a fear of violence or unwanted behaviour which is causing them alarm or distress. Also covers client who have previously taken action to stop harassment (i.e. sought an injunction) but this is not being complied with." %}</data>
      <data key="d10" xml:space="preserve">n209</data>
      </node>
    <node id="n202">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">family</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n210</data>
      </node>
    <node id="n203">
      <data key="d3" xml:space="preserve">{% trans "The client's problem is about admissions" %}</data>
      <data key="d4" xml:space="preserve">Admissions</data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d10" xml:space="preserve">n211</data>
      </node>
    <node id="n204">
      <data key="d3" xml:space="preserve">{% trans "The client's problem is about bullying, and none of the other issues above apply" %}</data>
      <data key="d4" xml:space="preserve">Bullying</data>
      <data key="d7" xml:space="preserve">9</data>
      <data key="d10" xml:space="preserve">n212</data>
      </node>
    <node id="n205">
      <data key="d3" xml:space="preserve">{% trans "A child or young person is out of school or in a Pupil Referral Unit, or is not receiving full-time education" %}</data>
      <data key="d4" xml:space="preserve">Child out of school</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n213</data>
      </node>
    <node id="n206">
      <data key="d3" xml:space="preserve">{% trans "The client's problem is about exclusion from school" %}</data>
      <data key="d4" xml:space="preserve">Exclusions</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n214</data>
      </node>
    <node id="n207">
      <data key="d3" xml:space="preserve">{% trans "The client's problem is about further education" %}</data>
      <data key="d4" xml:space="preserve">Further education</data>
      <data key="d7" xml:space="preserve">5</data>
      <data key="d10" xml:space="preserve">n215</data>
      </node>
    <node id="n208">
      <data key="d3" xml:space="preserve">{% blocktrans %}The problem is about a school, college or local authority's failure to
provide for a child or young person's educational needs, or specifically about the failure to provide the support set out in the assessment of their needs{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">Failure to provide support</data>
      <data key="d7" xml:space="preserve">6</data>
      <data key="d10" xml:space="preserve">n216</data>
      </node>
    <node id="n209">
      <data key="d3" xml:space="preserve">{% trans "The client's problem is about higher education" %}</data>
      <data key="d4" xml:space="preserve">Higher education</data>
      <data key="d7" xml:space="preserve">7</data>
      <data key="d10" xml:space="preserve">n217</data>
      </node>
    <node id="n210">
      <data key="d3" xml:space="preserve">{% trans "None of the above" %}</data>
      <data key="d4" xml:space="preserve">None of the above</data>
      <data key="d10" xml:space="preserve">n218</data>
      </node>
    <node id="n211">
      <data key="d3" xml:space="preserve">{% trans "The client's problem is about transport" %}</data>
      <data key="d4" xml:space="preserve">Transport</data>
      <data key="d7" xml:space="preserve">8</data>
      <data key="d10" xml:space="preserve">n219</data>
      </node>
    <node id="n212">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n220</data>
      </node>
    <node id="n213">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n221</data>
      </node>
    <node id="n214">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n222</data>
      </node>
    <node id="n215">
      <data key="d3" xml:space="preserve">{% trans "Any other issue" %}</data>
      <data key="d4" xml:space="preserve">Any other issue</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n223</data>
      </node>
    <node id="n216">
      <data key="d3" xml:space="preserve">{% trans "The client is enquiring about an application or admissions appeal in the normal admissions round (ie reception and secondary school transfers)" %}</data>
      <data key="d4" xml:space="preserve">Normal admissions round</data>
      <data key="d10" xml:space="preserve">n224</data>
      </node>
    <node id="n217">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n225</data>
      </node>
    <node id="n218">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n226</data>
      </node>
    <node id="n219">
      <data key="d3" xml:space="preserve">{% trans "Negligence in the provision of education" %}</data>
      <data key="d4" xml:space="preserve">Education negligence</data>
      <data key="d7" xml:space="preserve">4</data>
      <data key="d10" xml:space="preserve">n227</data>
      </node>
    <node id="n220">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n228</data>
      </node>
    <node id="n221">
      <data key="d3" xml:space="preserve">{% trans "The client's problem relates to special needs not being met properly for a child of compulsory school age, or a young person in compulsory or further education" %}</data>
      <data key="d4" xml:space="preserve">SEN negligence</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n229</data>
      </node>
    <node id="n222">
      <data key="d3" xml:space="preserve">{% trans "Any other problem" %}</data>
      <data key="d4" xml:space="preserve">Education negligence</data>
      <data key="d10" xml:space="preserve">n230</data>
      </node>
    <node id="n223">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n231</data>
      </node>
    <node id="n224">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n232</data>
      </node>
    <node id="n225">
      <data key="d3" xml:space="preserve">{% trans "There has been a formal fixed term exclusion from school (a suspension) of up to five days and the child has not received more than one other fixed term exclusion in the last school year" %}</data>
      <data key="d4" xml:space="preserve">Suspension</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n233</data>
      </node>
    <node id="n226">
      <data key="d3" xml:space="preserve">{% trans "Other" %}</data>
      <data key="d4" xml:space="preserve">Other</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n234</data>
      </node>
    <node id="n227">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n235</data>
      </node>
    <node id="n228">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n236</data>
      </node>
    <node id="n229">
      <data key="d3" xml:space="preserve">{% trans "Other" %}</data>
      <data key="d4" xml:space="preserve">Other</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n237</data>
      </node>
    <node id="n230">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n238</data>
      </node>
    <node id="n231">
      <data key="d3" xml:space="preserve">{% trans "The client's problem is about SEN, transport, admissions or exclusions" %}</data>
      <data key="d4" xml:space="preserve">SEN, transport etc</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n239</data>
      </node>
    <node id="n232">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n240</data>
      </node>
    <node id="n233">
      <data key="d3" xml:space="preserve">{% trans "The client's problem is about fees or funding" %}</data>
      <data key="d4" xml:space="preserve">Fees or funding</data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d10" xml:space="preserve">n241</data>
      </node>
    <node id="n234">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n242</data>
      </node>
    <node id="n235">
      <data key="d3" xml:space="preserve">{% trans "The client's problem is about admissions" %}</data>
      <data key="d4" xml:space="preserve">Admissions case</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n243</data>
      </node>
    <node id="n236">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n244</data>
      </node>
    <node id="n237">
      <data key="d3" xml:space="preserve">{% trans "The client's problem is about exclusion - but not for failure at exams or malpractice allegations eg plagiarism" %}</data>
      <data key="d4" xml:space="preserve">Exclusion case</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n245</data>
      </node>
    <node id="n238">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n246</data>
      </node>
    <node id="n239">
      <data key="d3" xml:space="preserve">{% trans "Any other problem" %}</data>
      <data key="d4" xml:space="preserve">Other</data>
      <data key="d10" xml:space="preserve">n247</data>
      </node>
    <node id="n240">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n248</data>
      </node>
    <node id="n241">
      <data key="d3" xml:space="preserve">{% trans "Pregnancy or maternity" %}</data>
      <data key="d4" xml:space="preserve">Disability Pregnancy</data>
      <data key="d7" xml:space="preserve">4</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}This refers to:
* pregnancy
* having recently given birth (and can include the need to breastfeed){% endblocktrans %}</data>
      <data key="d9" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">n249</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n242">
      <data key="d3" xml:space="preserve">{% trans "Race" %}</data>
      <data key="d4" xml:space="preserve">Race</data>
      <data key="d7" xml:space="preserve">7</data>
      <data key="d8" xml:space="preserve">{% trans "Race refers to a group of people defined by their race, colour, nationality (including citizenship), ethnic or national origins." %}</data>
      <data key="d9" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">n250</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n243">
      <data key="d3" xml:space="preserve">{% trans "Religion or belief (or lack of belief)" %}</data>
      <data key="d4" xml:space="preserve">Disability Pregnancy</data>
      <data key="d7" xml:space="preserve">8</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}Religion refers to any religious or philosophical belief. This also includes a lack of religious belief (eg atheism).
Generally, a belief should affect your life choices or the way you live for it to be included in the definition.{% endblocktrans %}</data>
      <data key="d9" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">n251</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n244">
      <data key="d3" xml:space="preserve">{% trans "Sex" %}</data>
      <data key="d4" xml:space="preserve">sex</data>
      <data key="d7" xml:space="preserve">9</data>
      <data key="d9" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">n252</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n245">
      <data key="d3" xml:space="preserve">{% trans "Sexual orientation" %}</data>
      <data key="d4" xml:space="preserve">sexual orientation</data>
      <data key="d7" xml:space="preserve">10</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}Sexual orientation is whether a person's sexual attraction is towards their own sex, the opposite sex or to both sexes.
This can also cover situations where discrimination is based on perceived sexual orientation, which may not be the case.{% endblocktrans %}</data>
      <data key="d9" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">n253</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n246">
      <data key="d3" xml:space="preserve">{% trans "Gender reassignment" %}</data>
      <data key="d4" xml:space="preserve">gender reassignment</data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}It is unlawful to discriminate against someone due to their gender reassignment.

This includes where someone is:
* is proposing to undergo gender reassignment
* is currently undergoing gender reassignment
* has already undergone (or partially undergone) the process of gender reassignment{% endblocktrans %}</data>
      <data key="d9" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">n254</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n247">
      <data key="d3" xml:space="preserve">{% trans "Pregnancy or maternity" %}</data>
      <data key="d4" xml:space="preserve">Discrimination due to pregnancy or having a child</data>
      <data key="d7" xml:space="preserve">5</data>
      <data key="d9" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">n255</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n248">
      <data key="d3" xml:space="preserve">{% trans "Disability or failure to make reasonable adjustments for a disabled person" %}</data>
      <data key="d4" xml:space="preserve">Disability Pregnancy</data>
      <data key="d7" xml:space="preserve">6</data>
      <data key="d9" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">n256</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n249">
      <data key="d3" xml:space="preserve">{% trans "Public law" %}</data>
      <data key="d4" xml:space="preserve">Public Law</data>
      <data key="d7" xml:space="preserve">11</data>
      <data key="d10" xml:space="preserve">n257</data>
      </node>
    <node id="n250">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE DISCLAIME</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">publiclaw</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n258</data>
      </node>
    <node id="n251">
      <data key="d3" xml:space="preserve">{% trans "Community care" %}</data>
      <data key="d4" xml:space="preserve">Community Care</data>
      <data key="d7" xml:space="preserve">10</data>
      <data key="d10" xml:space="preserve">n259</data>
      </node>
    <node id="n252">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE DISCLAIME</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">commcare</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n260</data>
      </node>
    <node id="n253">
      <data key="d3" xml:space="preserve">{% trans "The client has been identified as homeless through a Community Care Assessment" %}</data>
      <data key="d4" xml:space="preserve">Community Care Assesment - Homeless</data>
      <data key="d7" xml:space="preserve">10</data>
      <data key="d10" xml:space="preserve">n261</data>
      </node>
    <node id="n254">
      <data key="d3" xml:space="preserve">{% trans "The client has not been identified as homeless through a Community Care Assessment" %}</data>
      <data key="d4" xml:space="preserve">ComCare: Not homeless</data>
      <data key="d7" xml:space="preserve">10</data>
      <data key="d10" xml:space="preserve">n262</data>
      </node>
    <node id="n255">
      <data key="d3" xml:space="preserve">{% trans "Client wants advice about international family maintenance" %}</data>
      <data key="d4" xml:space="preserve">International family maintenance</data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}Covers enforcement of maintenance orders made outside the UK. Clients who have obtained maintenance orders in one country can apply to have them registered and enforced in another country. 

So where a client wants to obtain an order outside the UK this will not be in scope.

**NOTE: These are very unusual cases.**{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n263</data>
      </node>
    <node id="n256">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">family</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n264</data>
      </node>
    <node id="n257">
      <data key="d3" xml:space="preserve">{% trans "None of the above" %}</data>
      <data key="d4" xml:space="preserve">none of the above</data>
      <data key="d7" xml:space="preserve">999</data>
      <data key="d10" xml:space="preserve">n265</data>
      </node>
    <node id="n258">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOF</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n266</data>
      </node>
    <node id="n259">
      <data key="d3" xml:space="preserve">{% trans "Other" %}</data>
      <data key="d4" xml:space="preserve">Other</data>
      <data key="d10" xml:space="preserve">n267</data>
      </node>
    <node id="n260">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOF</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">discrimination</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n268</data>
      </node>
    <node id="n261">
      <data key="d3" xml:space="preserve">{% trans "Discrimination" %}</data>
      <data key="d4" xml:space="preserve">Discrimination</data>
      <data key="d7" xml:space="preserve">4</data>
      <data key="d10" xml:space="preserve">n269</data>
      </node>
    <node id="n262">
      <data key="d3" xml:space="preserve">{% trans "None of the above" %}</data>
      <data key="d4" xml:space="preserve">Personal Injury</data>
      <data key="d6"/>
      <data key="d8" xml:space="preserve">{% trans "Not a Civil Legal Advice category or legal problem." %}</data>
      <data key="d10" xml:space="preserve">n270</data>
      </node>
    <node id="n263">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE DISCLA</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">none</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n271</data>
      </node>
    <node id="n264">
      <data key="d3" xml:space="preserve">{% blocktrans %}IMPORTANT: Where a client or a child is AT IMMEDIATE RISK OF ABUSE you must follow the Civil Legal Advice Child, Young Person and Adult at Risk of Abuse Policy. You may need to report the matter to protection services.

*Click 'Next' to continue*{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">REMEMBER: report</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n272</data>
      </node>
    <node id="n265">
      <data key="d3" xml:space="preserve">{% trans "Legal advice in support of family mediation" %}</data>
      <data key="d4" xml:space="preserve">Mediation</data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}Family mediation can help people whose relationships have broken down to reach their own agreement about money, property and childcare, without going to court.

If the client wants legal advice to support of ongoing or recently completed mediation process this will be in scope. This can include making any agreement reached in mediation legally binding by applying to the court (a consent order).

*Please note: Mediation must be ongoing or have concluded. Clients will not qualify for Civil Legal Advice advice where mediation has not yet taken place or they have only attended Mediation Assessment Information Meeting (MIAM).*{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n273</data>
      </node>
    <node id="n266">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">family</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n274</data>
      </node>
    <node id="n267">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read out the following to the client:


*Based on what you have told me today your problem may be covered by legal aid. But you will still need to show that you qualify financially.*

*I’m afraid that Civil Legal Advice does not provide advice about the issue that you are calling about. But our service is not your only option and I will direct you to alternative help.*

*I can’t guarantee that these organisations/this organisation will take on your case under legal aid so please check with them to see whether they are able to help you. If you do not qualify for legal aid you may have to pay for their service. So check any costs, their opening hours and whether you can make an appointment. Also check any insurance policies you may have that provide legal cover as any potential costs may be covered by this.*{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">Primary question: Cl</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n275</data>
      </node>
    <node id="n268">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n276</data>
      </node>
    <node id="n269">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n278</data>
      </node>
    <node id="n270">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n279</data>
      </node>
    <node id="n271">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n280</data>
      </node>
    <node id="n272">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n281</data>
      </node>
    <node id="n273">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n282</data>
      </node>
    <node id="n274">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n283</data>
      </node>
    <node id="n275">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n284</data>
      </node>
    <node id="n276">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n285</data>
      </node>
    <node id="n277">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n286</data>
      </node>
    <node id="n278">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n287</data>
      </node>
    <node id="n279">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n288</data>
      </node>
    <node id="n280">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n289</data>
      </node>
    <node id="n281">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n290</data>
      </node>
    <node id="n282">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n291</data>
      </node>
    <node id="n283">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n292</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n284">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n293</data>
      </node>
    <node id="n285">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n294</data>
      </node>
    <node id="n286">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.

We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]*{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">Public Law</data>
      <data key="d7" xml:space="preserve">11</data>
      <data key="d10" xml:space="preserve">n295</data>
      </node>
    <node id="n287">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.

We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]*{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">Public Law</data>
      <data key="d7" xml:space="preserve">11</data>
      <data key="d10" xml:space="preserve">n296</data>
      </node>
    <node id="n288">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.

We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]*{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">Public Law</data>
      <data key="d7" xml:space="preserve">11</data>
      <data key="d10" xml:space="preserve">n297</data>
      </node>
    <node id="n289">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.

We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]*{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">Public Law</data>
      <data key="d7" xml:space="preserve">11</data>
      <data key="d10" xml:space="preserve">n298</data>
      </node>
    <node id="n290">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.

We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]*{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">Public Law</data>
      <data key="d7" xml:space="preserve">11</data>
      <data key="d10" xml:space="preserve">n299</data>
      </node>
    <node id="n291">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.

We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]*{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">Public Law</data>
      <data key="d7" xml:space="preserve">11</data>
      <data key="d10" xml:space="preserve">n300</data>
      </node>
    <node id="n292">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.

We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]*{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">Public Law</data>
      <data key="d7" xml:space="preserve">11</data>
      <data key="d10" xml:space="preserve">n301</data>
      </node>
    <node id="n293">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.

We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]*{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">Public Law</data>
      <data key="d7" xml:space="preserve">11</data>
      <data key="d10" xml:space="preserve">n302</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n294">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.

We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]*{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">Public Law</data>
      <data key="d7" xml:space="preserve">11</data>
      <data key="d10" xml:space="preserve">n303</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n295">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.

We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]*{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">Public Law</data>
      <data key="d7" xml:space="preserve">11</data>
      <data key="d10" xml:space="preserve">n304</data>
      </node>
    <node id="n296">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.

We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]*{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">Public Law</data>
      <data key="d7" xml:space="preserve">11</data>
      <data key="d10" xml:space="preserve">n305</data>
      </node>
    <node id="n297">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n306</data>
      </node>
    <node id="n298">
      <data key="d3" xml:space="preserve">{% trans "Domestic abuse (including psychological, physical, financial, sexual or emotional abuse, forced marriage, child abduction, female genital mutilation and harassment). Also includes defence against a non-molestation or occupation order where the client is the alleged abuser." %}</data>
      <data key="d4" xml:space="preserve">Client wants to prev</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}Where a Client wants to seek a court order to protect themselves or a child from abuse via a court order 'an injunction' that tells a person they're not allowed to do a certain act.

Some clients who are the alleged abuser do not agree with the injunction against them and wish to get help in defending themselves against it.

Guidance contains an article "Domestic violence and abuse - definition" for more information. Search for 'dv' or 'abuse' to find it quickest.{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n307</data>
      </node>
    <node id="n299">
      <data key="d3" xml:space="preserve">{% trans "Forced marriage - the client wants advice" %}</data>
      <data key="d4" xml:space="preserve">Client wants to prev</data>
      <data key="d7" xml:space="preserve">6</data>
      <data key="d8" xml:space="preserve">{% trans "This is where a marriage is about to take place or has taken place without the full and free consent of each party. This may be due to actual or threats of physical force or violence, emotional pressure or psychological abuse. Civil Legal Advice Specialists can offer advice on seeking an order to protect the client from such a marriage occuring or how to end such a marriage." %}</data>
      <data key="d10" xml:space="preserve">n308</data>
      </node>
    <node id="n300">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">family</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n309</data>
      </node>
    <node id="n301">
      <data key="d3" xml:space="preserve">{% trans "Other" %}</data>
      <data key="d4" xml:space="preserve">Other</data>
      <data key="d10" xml:space="preserve">n310</data>
      </node>
    <node id="n302">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">family</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n311</data>
      </node>
    <node id="n303">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n312</data>
      </node>
    <node id="n304">
      <data key="d3" xml:space="preserve">{% blocktrans %}Is there a dispute for which family mediation is relevant? If so, please check if client has heard of/and considered Family Mediation.

*On the following screen please select if they want to find a local mediator, or that mediation isn't relevant to the problem. Click next to continue.*{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above (i</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}Family mediators are trained to work with people whose relationships have broken down. They will listen to both sides of the argument and help you to reach your own agreement about money, property and childcare, without going to court.

It is not just separating couples that can use mediation. It may also help grandparents or step-families resolve their issues.

Mediation provides a safe and neutral setting for you to talk and explore your concerns and needs to each other.

Search for 'Family Mediation' in the guidance search box for more help.

If you are qualify you can get legal aid for family mediation as well as legal advice to support the mediation process. This can include the cost of making any agreement that you reach in mediation legally binding by applying to the court - this is called applying for a consent order.{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n313</data>
      </node>
    <node id="n305">
      <data key="d3" xml:space="preserve">{% trans "Client wishes to find mediator." %}</data>
      <data key="d4" xml:space="preserve">None of the above (i</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n314</data>
      </node>
    <node id="n306">
      <data key="d3" xml:space="preserve">{% trans "Client does not wish to find a mediator." %}</data>
      <data key="d4" xml:space="preserve">None of the above (i</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n315</data>
      </node>
    <node id="n307">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*If you have Internet access I can tell you where to find more information about Family Mediation and how to search for a family mediator.*

*Or I can find a family mediation service for you now.*

*If you qualify you may be able to get legal aid to cover the costs of Family Mediation as well as legal advice to support the mediation process. Or you may need to pay for the service. Please speak to the mediation service to find out more.*

You should now direct the client to their nearest contracted quality assured family mediation service using the directory (Find An Adviser tool){% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n316</data>
      </node>
    <node id="n308">
      <data key="d3" xml:space="preserve">{% trans "The client has already taken action to stop domestic abuse (e.g. via an injunction) but needs to take further action as the order is not being complied with" %}</data>
      <data key="d4" xml:space="preserve">Client being harassed by partner or ex-partner</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n317</data>
      </node>
    <node id="n309">
      <data key="d3" xml:space="preserve">{% trans "Divorce, contact with children, finances between two individuals (private law)" %}</data>
      <data key="d4" xml:space="preserve">Private Law</data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d8" xml:space="preserve">{% trans "Between two or more individuals." %}</data>
      <data key="d10" xml:space="preserve">n318</data>
      </node>
    <node id="n310">
      <data key="d3" xml:space="preserve">{% trans "Divorce/Nullity/Dissolution" %}</data>
      <data key="d4" xml:space="preserve">Divorce</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}* Divorce - ending a marriage
* Nullity - declaring a marriage null and void so it is regarded not to have taken place
* Dissolution - ending a same sex Civil Partnership{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n319</data>
      </node>
    <node id="n311">
      <data key="d3" xml:space="preserve">{% trans "Children disputes (eg contact with children)" %}</data>
      <data key="d4" xml:space="preserve">Children disputes (a</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}Includes advice on the following areas

* Parental Responsibility
* Contact
* Residence
* Transferring status of Parentage{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n320</data>
      </node>
    <node id="n312">
      <data key="d3" xml:space="preserve">{% trans "Financial matters" %}</data>
      <data key="d4" xml:space="preserve">Financial matters</data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d8" xml:space="preserve">{% blocktrans %}Includes advice on financial disputes arising out of:

* Divorce/separation (including civil partnerships) including Inheritance and trusts of land
* Transfer of tenancies on divorce/separation
* Maintenance{% endblocktrans %}</data>
      <data key="d10" xml:space="preserve">n321</data>
      </node>
    <node id="n313">
      <data key="d3" xml:space="preserve">{% trans "Not a dispute for which mediation is relevant." %}</data>
      <data key="d4" xml:space="preserve">None of the above (i</data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d10" xml:space="preserve">n322</data>
      </node>
    <node id="n314">
      <data key="d3" xml:space="preserve">{% trans "Domestic abuse (or their abuser has a criminal conviction)" %}</data>
      <data key="d4" xml:space="preserve">Client has been subj</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n323</data>
      </node>
    <node id="n315">
      <data key="d3" xml:space="preserve">{% trans "The client's child has experienced child abuse within the family, or the abuser has a criminal conviction (remember that if the caller is the abuser, this will not be in scope)" %}</data>
      <data key="d4" xml:space="preserve">Relationship has inv</data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d10" xml:space="preserve">n324</data>
      </node>
    <node id="n316">
      <data key="d3" xml:space="preserve">{% trans "The client is under 18" %}</data>
      <data key="d4" xml:space="preserve">Client is under 18</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n325</data>
      </node>
    <node id="n317">
      <data key="d3" xml:space="preserve">{% trans "No abuse." %}</data>
      <data key="d4" xml:space="preserve">Client is under 18</data>
      <data key="d7" xml:space="preserve">4</data>
      <data key="d10" xml:space="preserve">n326</data>
      </node>
    <node id="n318">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">family</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n327</data>
      </node>
    <node id="n319">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*"We may be able to put you through to a legal adviser who could help you with this area of law, before I can transfer you we need to complete a short financial assessment to see if you can get legal aid."*

*Please note that before a legal adviser can assist you, you will need to provide proof of what you have told me about today. They will explain to you what you can use as proof."*{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n328</data>
      </node>
    <node id="n320">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">family</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n329</data>
      </node>
    <node id="n321">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read out the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.

We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]*{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">Primary question: Cl</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n330</data>
      </node>
    <node id="n322">
      <data key="d3" xml:space="preserve">{% trans "The matter relates to a child in care, a care leaver, or the call is made by a foster carer." %}</data>
      <data key="d4" xml:space="preserve">Child in care</data>
      <data key="d7" xml:space="preserve">5</data>
      <data key="d10" xml:space="preserve">n331</data>
      </node>
    <node id="n323">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n332</data>
      </node>
    <node id="n324">
      <data key="d3" xml:space="preserve">{% trans "The client may have been discriminated against (select this button to proceed to the discrimination category)" %}</data>
      <data key="d4" xml:space="preserve">Discrimination?</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n334</data>
      </node>
    <node id="n325">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n335</data>
      </node>
    <node id="n326">
      <data key="d3" xml:space="preserve">{% trans "Female genital mutilation - the client is worried they may become a victim" %}</data>
      <data key="d4" xml:space="preserve">FGM</data>
      <data key="d7" xml:space="preserve">7</data>
      <data key="d10" xml:space="preserve">n336</data>
      </node>
    <node id="n327">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">family</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n337</data>
      </node>
    <node id="n328">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n338</data>
      </node>
    <node id="n329">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d10" xml:space="preserve">n339</data>
      </node>
    <node id="n330">
      <data key="d3" xml:space="preserve">{% trans "International child abduction – The client lives abroad but their child has been taken to the UK" %}</data>
      <data key="d4" xml:space="preserve"/>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n340</data>
      </node>
    <node id="n331">
      <data key="d3" xml:space="preserve">{% trans "Any other child abduction problem" %}</data>
      <data key="d4" xml:space="preserve"/>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d8" xml:space="preserve">{% trans "Seeking protection from the unlawful removal of a child from the UK or the return of a child who has been unlawfully removed from the UK or unlawfully removed within the UK. A child is someone under 18 and the client must be the parent or someone with parental responsibility for that child." %}</data>
      <data key="d10" xml:space="preserve">n341</data>
      </node>
    <node id="n332">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">family</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n342</data>
      </node>
    <node id="n333">
      <data key="d3" xml:space="preserve">{% trans "No financial assessment is needed for this problem." %}</data>
      <data key="d4" xml:space="preserve"/>
      <data key="d10" xml:space="preserve">n343</data>
      </node>
    <node id="n334">
      <data key="d3" xml:space="preserve">{% trans "The client’s social landlord intends to get (or has got) an Antisocial Behaviour Order or Antisocial Behaviour Injunction against the client or someone living with them." %}</data>
      <data key="d4" xml:space="preserve">Social landlord</data>
      <data key="d6"/>
      <data key="d9" xml:space="preserve">{% trans "Select the option that best describes the client’s situation." %}</data>
      <data key="d10" xml:space="preserve">n80</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n335">
      <data key="d3" xml:space="preserve">{% trans "Client has private landlord" %}</data>
      <data key="d4" xml:space="preserve">Private landlord</data>
      <data key="d6"/>
      <data key="d10" xml:space="preserve">n87</data>
      </node>
    <node id="n336">
      <data key="d3" xml:space="preserve">{% trans "Client has received an ASBO/ASBI and wishes to challenge" %}</data>
      <data key="d4" xml:space="preserve">Client has received </data>
      <data key="d6"/>
      <data key="d10" xml:space="preserve">n85</data>
      </node>
    <node id="n337">
      <data key="d3" xml:space="preserve">{% trans "Court has issued notice of ASBO/ASBI proceedings" %}</data>
      <data key="d4" xml:space="preserve">Court has issued not</data>
      <data key="d6"/>
      <data key="d10" xml:space="preserve">n83</data>
      </node>
    <node id="n338">
      <data key="d3" xml:space="preserve">{% trans "Client has received a letter from their social landlord (including local authorities) confirming an intention to apply for an ASBO or ASBI" %}</data>
      <data key="d4" xml:space="preserve">Client has received </data>
      <data key="d6"/>
      <data key="d10" xml:space="preserve">n81</data>
      </node>
    <node id="n339">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on.  However we can provide alternative contact details of organisations who may be able to assist you.*

*We can provide helplines, websites or F2F however please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?*

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">None of the above, a</data>
      <data key="d6"/>
      <data key="d10" xml:space="preserve">n277</data>
      </node>
    <node id="n340">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n84</data>
      </node>
    <node id="n341">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n82</data>
      </node>
    <node id="n342">
      <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d4" xml:space="preserve">OUTOFSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">housing</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n88</data>
      </node>
    <node id="n343">
      <data key="d3" xml:space="preserve">{% trans "Yes" %}</data>
      <data key="d4" xml:space="preserve">Yes</data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d9" xml:space="preserve">{% trans "Does the client have any of the following?" %}</data>
      <data key="d10" xml:space="preserve">n401</data>
      <data key="d12" xml:space="preserve">The client is the parent of the child or someone with parental responsibility</data>
      </node>
    <node id="n344">
      <data key="d3" xml:space="preserve">{% trans "No" %}</data>
      <data key="d4" xml:space="preserve">No</data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d10" xml:space="preserve">n402</data>
      <data key="d12" xml:space="preserve">**The client is not a parent or guardian of the child**

A financial assessment will need to be completed.</data>
      </node>
    <node id="n345">
      <data key="d3" xml:space="preserve">{% trans "Letter of proceedings" %}</data>
      <data key="d4" xml:space="preserve">Letter of proceedings</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
  <finance xml:space="preserve">passported</finance>
</context>
      </data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n403</data>
      <data key="d12" xml:space="preserve">**The client has received a letter of proceedings, letter of issue or have a court date.**

No financial assessment is required.</data>
      </node>
    <node id="n346">
      <data key="d3" xml:space="preserve">{% trans "Letter of issue" %}</data>
      <data key="d4" xml:space="preserve">Letter of issue</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
  <finance xml:space="preserve">passported</finance>
</context>
      </data>
      <data key="d7" xml:space="preserve">2</data>
      <data key="d9" xml:space="preserve">{% trans "Does the client have any of the following?" %}</data>
      <data key="d10" xml:space="preserve">n404</data>
      <data key="d12" xml:space="preserve">**The client has received a letter of proceedings, letter of issue or have a court date.**

No financial assessment is required.</data>
      </node>
    <node id="n347">
      <data key="d3" xml:space="preserve">{% trans "Date to attend court" %}</data>
      <data key="d4" xml:space="preserve">Date to attend court</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
  <finance xml:space="preserve">passported</finance>
</context>
      </data>
      <data key="d7" xml:space="preserve">3</data>
      <data key="d9" xml:space="preserve">{% trans "Does the client have any of the following?" %}</data>
      <data key="d10" xml:space="preserve">n405</data>
      <data key="d12" xml:space="preserve">**The client has received a letter of proceedings, letter of issue or have a court date.**

No financial assessment is required.</data>
      </node>
    <node id="n348">
      <data key="d3" xml:space="preserve">{% trans "None of the above" %}</data>
      <data key="d4" xml:space="preserve">None of the above</data>
      <data key="d7" xml:space="preserve">4</data>
      <data key="d9" xml:space="preserve">{% trans "Does the client have any of the following?" %}</data>
      <data key="d10" xml:space="preserve">n406</data>
      <data key="d12" xml:space="preserve">**The client has not received a letter of proceedings, letter of issue or have a court date.**

A financial assessment will need to be completed.</data>
      </node>
    <node id="n349">
      <data key="d3" xml:space="preserve">{% trans "Parent is a foster carer or an approved prospective adoptive parent  or for a former foster parent of a young person who continues to reside with their former foster carer making an application to the first tier tribunal in a SEND case" %}</data>
      <data key="d4" xml:space="preserve">Parent is a foster carer or</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
<finance xml:space="preserve">passported</finance>
</context>
      </data>
      <data key="d7" xml:space="preserve">1</data>
      <data key="d10" xml:space="preserve">n349</data>
      <data key="d12" xml:space="preserve">**Parent is a foster carer or an approved prospective adoptive parent  or for a former foster parent of a young person who continues to reside with their former foster carer making an application to the first tier tribunal in a SEND case.**

No financial assessment is required.</data>
      </node>
    <node id="n350">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">education</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n350</data>
      </node>
    <node id="n351">
      <data key="d3" xml:space="preserve">{% trans "Special Guardianship Order" %}</data>
      <data key="d4" xml:space="preserve">Special Guardianship Order</data>
      <data key="d10" xml:space="preserve">n410</data>
      </node>
    <node id="n352">
      <data key="d3" xml:space="preserve">{% trans "Parent, or person with parental responsibility, opposing or seeking to discharge a Special Guardianship Order" %}</data>
      <data key="d4" xml:space="preserve">Parent</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">   <finance xml:space="preserve">passported</finance> </context>
      </data>
      <data key="d10" xml:space="preserve">n411</data>
      </node>
    <node id="n353">
      <data key="d3" xml:space="preserve">{% trans "Any other person seeking a Special Guardianship Order, or seeking to discharge an order" %}</data>
      <data key="d4" xml:space="preserve">Other person</data>
      <data key="d10" xml:space="preserve">n412</data>
      </node>
    <node id="n354">
      <data key="d3" xml:space="preserve">INSCOPE</data>
      <data key="d4" xml:space="preserve">INSCOPE</data>
      <data key="d6" xml:space="preserve">
        <context xmlns="" xml:space="preserve">
	<category xml:space="preserve">family</category>
</context>
      </data>
      <data key="d10" xml:space="preserve">n413</data>
      </node>
    <node id="n355">
      <data key="d3" xml:space="preserve">{% trans "The client came to CLA through any other route" %}</data>
      <data key="d4" xml:space="preserve">Client not subject t</data>
      <data key="d10" xml:space="preserve">n188</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n356">
      <data key="d3" xml:space="preserve">{% blocktrans %}Please read the following to the client:

*Based on the information you have provided the issue you are calling about isn’t something CLA can provide advice on. However we can provide alternative contact details of organisations who may be able to assist you.

We can provide helplines, websites or a Legal Aid provider outside of the South West of England who may be able to assist you over the telephone. However please be aware that you may have to pay for that service. Do you have any preference on the alternative help we provide today?

[Discussion on best options, paid v free, website calls, national services, local services, read from websites etc. Give details of organisations.

Remember to record details of the conversation in your CHS notes.]*{% endblocktrans %}</data>
      <data key="d4" xml:space="preserve">Public Law</data>
      <data key="d7" xml:space="preserve">11</data>
      <data key="d10" xml:space="preserve">n351</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <node id="n357">
      <data key="d3" xml:space="preserve">{% trans "The client was referred to CLA by a provider or agency in the South West of England who could not assist them" %}</data>
      <data key="d4" xml:space="preserve">Client not subject t</data>
      <data key="d8" xml:space="preserve">{% trans "South West of England consists of the counties of Cornwall (including the Isles of Scilly), Dorset, Devon, Gloucestershire, Somerset and Wiltshire" %}</data>
      <data key="d10" xml:space="preserve">n190</data>
      <data key="d11" xml:space="preserve"/>
      </node>
    <edge id="e0" source="n1" target="n2">
      </edge>
    <edge id="e1" source="n2" target="n3">
      </edge>
    <edge id="e2" source="n3" target="n4">
      </edge>
    <edge id="e3" source="n5" target="n6">
      </edge>
    <edge id="e4" source="n7" target="n8">
      </edge>
    <edge id="e5" source="n9" target="n10">
      </edge>
    <edge id="e6" source="n3" target="n11">
      </edge>
    <edge id="e7" source="n12" target="n13">
      </edge>
    <edge id="e8" source="n14" target="n15">
      </edge>
    <edge id="e9" source="n3" target="n17">
      </edge>
    <edge id="e10" source="n18" target="n19">
      </edge>
    <edge id="e11" source="n20" target="n21">
      </edge>
    <edge id="e12" source="n22" target="n23">
      </edge>
    <edge id="e13" source="n2" target="n24">
      </edge>
    <edge id="e14" source="n24" target="n25">
      </edge>
    <edge id="e15" source="n26" target="n27">
      </edge>
    <edge id="e16" source="n28" target="n29">
      </edge>
    <edge id="e17" source="n30" target="n31">
      </edge>
    <edge id="e18" source="n32" target="n33">
      </edge>
    <edge id="e19" source="n34" target="n35">
      </edge>
    <edge id="e20" source="n36" target="n37">
      </edge>
    <edge id="e21" source="n38" target="n39">
      </edge>
    <edge id="e22" source="n40" target="n41">
      </edge>
    <edge id="e23" source="n24" target="n43">
      </edge>
    <edge id="e24" source="n43" target="n44">
      </edge>
    <edge id="e25" source="n44" target="n45">
      </edge>
    <edge id="e26" source="n2" target="n46">
      </edge>
    <edge id="e27" source="n47" target="n48">
      </edge>
    <edge id="e28" source="n48" target="n49">
      </edge>
    <edge id="e29" source="n50" target="n51">
      </edge>
    <edge id="e30" source="n52" target="n53">
      </edge>
    <edge id="e31" source="n54" target="n55">
      </edge>
    <edge id="e32" source="n56" target="n57">
      </edge>
    <edge id="e33" source="n58" target="n59">
      </edge>
    <edge id="e34" source="n60" target="n61">
      </edge>
    <edge id="e35" source="n62" target="n63">
      </edge>
    <edge id="e36" source="n64" target="n65">
      </edge>
    <edge id="e37" source="n66" target="n67">
      </edge>
    <edge id="e38" source="n68" target="n69">
      </edge>
    <edge id="e39" source="n2" target="n70">
      </edge>
    <edge id="e40" source="n2" target="n72">
      </edge>
    <edge id="e41" source="n1" target="n73">
      </edge>
    <edge id="e42" source="n73" target="n74">
      </edge>
    <edge id="e43" source="n75" target="n76">
      </edge>
    <edge id="e44" source="n77" target="n78">
      </edge>
    <edge id="e45" source="n73" target="n79">
      </edge>
    <edge id="e46" source="n73" target="n81">
      </edge>
    <edge id="e47" source="n81" target="n82">
      </edge>
    <edge id="e48" source="n82" target="n83">
      </edge>
    <edge id="e49" source="n81" target="n84">
      </edge>
    <edge id="e50" source="n84" target="n85">
      </edge>
    <edge id="e51" source="n81" target="n86">
      </edge>
    <edge id="e52" source="n73" target="n88">
      </edge>
    <edge id="e53" source="n1" target="n89">
      </edge>
    <edge id="e54" source="n89" target="n94">
      </edge>
    <edge id="e55" source="n1" target="n98">
      </edge>
    <edge id="e56" source="n99" target="n100">
      </edge>
    <edge id="e57" source="n102" target="n103">
      </edge>
    <edge id="e58" source="n104" target="n105">
      </edge>
    <edge id="e59" source="n106" target="n107">
      </edge>
    <edge id="e60" source="n108" target="n109">
      </edge>
    <edge id="e61" source="n110" target="n111">
      </edge>
    <edge id="e62" source="n112" target="n113">
      </edge>
    <edge id="e63" source="n114" target="n115">
      </edge>
    <edge id="e64" source="n117" target="n118">
      </edge>
    <edge id="e65" source="n119" target="n120">
      </edge>
    <edge id="e66" source="n121" target="n122">
      </edge>
    <edge id="e67" source="n126" target="n127">
      </edge>
    <edge id="e68" source="n128" target="n129">
      </edge>
    <edge id="e69" source="n130" target="n131">
      </edge>
    <edge id="e70" source="n132" target="n133">
      </edge>
    <edge id="e71" source="n134" target="n135">
      </edge>
    <edge id="e72" source="n139" target="n140">
      </edge>
    <edge id="e73" source="n99" target="n143">
      </edge>
    <edge id="e74" source="n99" target="n144">
      </edge>
    <edge id="e75" source="n99" target="n145">
      </edge>
    <edge id="e76" source="n1" target="n0">
      </edge>
    <edge id="e77" source="n0" target="n146">
      </edge>
    <edge id="e78" source="n146" target="n147">
      </edge>
    <edge id="e79" source="n0" target="n148">
      </edge>
    <edge id="e80" source="n148" target="n149">
      </edge>
    <edge id="e81" source="n0" target="n150">
      </edge>
    <edge id="e82" source="n150" target="n151">
      </edge>
    <edge id="e83" source="n150" target="n153">
      </edge>
    <edge id="e84" source="n150" target="n155">
      </edge>
    <edge id="e85" source="n1" target="n157">
      </edge>
    <edge id="e86" source="n157" target="n158">
      </edge>
    <edge id="e87" source="n157" target="n324">
      </edge>
    <edge id="e88" source="n157" target="n160">
      </edge>
    <edge id="e89" source="n1" target="n162">
      </edge>
    <edge id="e90" source="n162" target="n163">
      </edge>
    <edge id="e91" source="n162" target="n164">
      </edge>
    <edge id="e92" source="n1" target="n166">
      </edge>
    <edge id="e93" source="n166" target="n167">
      </edge>
    <edge id="e94" source="n166" target="n168">
      </edge>
    <edge id="e95" source="n1" target="n170">
      </edge>
    <edge id="e96" source="n170" target="n171">
      </edge>
    <edge id="e97" source="n170" target="n172">
      </edge>
    <edge id="e98" source="n1" target="n174">
      </edge>
    <edge id="e99" source="n1" target="n176">
      </edge>
    <edge id="e100" source="n1" target="n178">
      </edge>
    <edge id="e101" source="n181" target="n182">
      </edge>
    <edge id="e102" source="n1" target="n183">
      </edge>
    <edge id="e103" source="n1" target="n185">
      </edge>
    <edge id="e104" source="n42" target="n187">
      </edge>
    <edge id="e105" source="n42" target="n188">
      </edge>
    <edge id="e106" source="n72" target="n190">
      </edge>
    <edge id="e107" source="n72" target="n191">
      </edge>
    <edge id="e108" source="n191" target="n193">
      </edge>
    <edge id="e109" source="n191" target="n192">
      </edge>
    <edge id="e110" source="n3" target="n194">
      </edge>
    <edge id="e111" source="n98" target="n99">
      </edge>
    <edge id="e112" source="n199" target="n200">
      </edge>
    <edge id="e113" source="n152" target="n203">
      </edge>
    <edge id="e114" source="n152" target="n204">
      </edge>
    <edge id="e115" source="n152" target="n205">
      </edge>
    <edge id="e116" source="n152" target="n206">
      </edge>
    <edge id="e117" source="n152" target="n208">
      </edge>
    <edge id="e118" source="n152" target="n207">
      </edge>
    <edge id="e119" source="n152" target="n209">
      </edge>
    <edge id="e120" source="n152" target="n211">
      </edge>
    <edge id="e121" source="n152" target="n210">
      </edge>
    <edge id="e122" source="n205" target="n212">
      </edge>
    <edge id="e123" source="n208" target="n213">
      </edge>
    <edge id="e124" source="n204" target="n325">
      </edge>
    <edge id="e125" source="n203" target="n215">
      </edge>
    <edge id="e126" source="n203" target="n216">
      </edge>
    <edge id="e127" source="n215" target="n218">
      </edge>
    <edge id="e128" source="n152" target="n219">
      </edge>
    <edge id="e129" source="n211" target="n220">
      </edge>
    <edge id="e130" source="n219" target="n221">
      </edge>
    <edge id="e131" source="n219" target="n222">
      </edge>
    <edge id="e132" source="n206" target="n226">
      </edge>
    <edge id="e133" source="n206" target="n225">
      </edge>
    <edge id="e134" source="n226" target="n227">
      </edge>
    <edge id="e135" source="n207" target="n229">
      </edge>
    <edge id="e136" source="n231" target="n232">
      </edge>
    <edge id="e137" source="n207" target="n231">
      </edge>
    <edge id="e138" source="n233" target="n234">
      </edge>
    <edge id="e139" source="n235" target="n236">
      </edge>
    <edge id="e140" source="n237" target="n238">
      </edge>
    <edge id="e141" source="n209" target="n233">
      </edge>
    <edge id="e142" source="n209" target="n235">
      </edge>
    <edge id="e143" source="n209" target="n237">
      </edge>
    <edge id="e144" source="n209" target="n239">
      </edge>
    <edge id="e145" source="n178" target="n181">
      </edge>
    <edge id="e146" source="n178" target="n179">
      </edge>
    <edge id="e147" source="n221" target="n223">
      </edge>
    <edge id="e148" source="n0" target="n152">
      </edge>
    <edge id="e149" source="n99" target="n247">
      </edge>
    <edge id="e150" source="n99" target="n248">
      </edge>
    <edge id="e151" source="n1" target="n249">
      </edge>
    <edge id="e152" source="n1" target="n251">
      </edge>
    <edge id="e153" source="n251" target="n253">
      </edge>
    <edge id="e154" source="n251" target="n254">
      </edge>
    <edge id="e155" source="n253" target="n69">
      </edge>
    <edge id="e156" source="n255" target="n256">
      </edge>
    <edge id="e157" source="n73" target="n261">
      </edge>
    <edge id="e158" source="n1" target="n262">
      </edge>
    <edge id="e159" source="n90" target="n264">
      </edge>
    <edge id="e160" source="n264" target="n91">
      </edge>
    <edge id="e161" source="n158" target="n267">
      </edge>
    <edge id="e162" source="n267" target="n159">
      </edge>
    <edge id="e163" source="n88" target="n268">
      </edge>
    <edge id="e164" source="n196" target="n269">
      </edge>
    <edge id="e165" source="n269" target="n197">
      </edge>
    <edge id="e166" source="n16" target="n270">
      </edge>
    <edge id="e167" source="n194" target="n270">
      </edge>
    <edge id="e168" source="n270" target="n195">
      </edge>
    <edge id="e169" source="n193" target="n271">
      </edge>
    <edge id="e170" source="n271" target="n198">
      </edge>
    <edge id="e171" source="n188" target="n272">
      </edge>
    <edge id="e172" source="n272" target="n189">
      </edge>
    <edge id="e173" source="n192" target="n272">
      </edge>
    <edge id="e174" source="n216" target="n273">
      </edge>
    <edge id="e175" source="n273" target="n217">
      </edge>
    <edge id="e176" source="n225" target="n274">
      </edge>
    <edge id="e177" source="n274" target="n228">
      </edge>
    <edge id="e178" source="n222" target="n275">
      </edge>
    <edge id="e179" source="n275" target="n224">
      </edge>
    <edge id="e180" source="n229" target="n276">
      </edge>
    <edge id="e181" source="n276" target="n230">
      </edge>
    <edge id="e182" source="n210" target="n276">
      </edge>
    <edge id="e183" source="n277" target="n240">
      </edge>
    <edge id="e184" source="n239" target="n277">
      </edge>
    <edge id="e185" source="n86" target="n278">
      </edge>
    <edge id="e186" source="n278" target="n87">
      </edge>
    <edge id="e187" source="n279" target="n97">
      </edge>
    <edge id="e188" source="n70" target="n280">
      </edge>
    <edge id="e189" source="n280" target="n71">
      </edge>
    <edge id="e190" source="n257" target="n281">
      </edge>
    <edge id="e191" source="n281" target="n258">
      </edge>
    <edge id="e192" source="n123" target="n282">
      </edge>
    <edge id="e193" source="n282" target="n124">
      </edge>
    <edge id="e194" source="n136" target="n283">
      </edge>
    <edge id="e195" source="n283" target="n137">
      </edge>
    <edge id="e196" source="n141" target="n284">
      </edge>
    <edge id="e197" source="n284" target="n142">
      </edge>
    <edge id="e198" source="n259" target="n285">
      </edge>
    <edge id="e199" source="n285" target="n260">
      </edge>
    <edge id="e200" source="n249" target="n286">
      </edge>
    <edge id="e201" source="n286" target="n250">
      </edge>
    <edge id="e202" source="n174" target="n287">
      </edge>
    <edge id="e203" source="n287" target="n175">
      </edge>
    <edge id="e204" source="n262" target="n288">
      </edge>
    <edge id="e205" source="n288" target="n263">
      </edge>
    <edge id="e206" source="n176" target="n289">
      </edge>
    <edge id="e207" source="n289" target="n177">
      </edge>
    <edge id="e208" source="n185" target="n290">
      </edge>
    <edge id="e209" source="n290" target="n186">
      </edge>
    <edge id="e210" source="n254" target="n291">
      </edge>
    <edge id="e211" source="n291" target="n252">
      </edge>
    <edge id="e212" source="n164" target="n294">
      </edge>
    <edge id="e213" source="n294" target="n165">
      </edge>
    <edge id="e214" source="n172" target="n295">
      </edge>
    <edge id="e215" source="n295" target="n173">
      </edge>
    <edge id="e216" source="n168" target="n296">
      </edge>
    <edge id="e217" source="n296" target="n169">
      </edge>
    <edge id="e218" source="n268" target="n297">
      </edge>
    <edge id="e219" source="n183" target="n292">
      </edge>
    <edge id="e220" source="n292" target="n184">
      </edge>
    <edge id="e221" source="n89" target="n298">
      </edge>
    <edge id="e222" source="n298" target="n90">
      </edge>
    <edge id="e223" source="n298" target="n92">
      </edge>
    <edge id="e224" source="n201" target="n202">
      </edge>
    <edge id="e225" source="n299" target="n300">
      </edge>
    <edge id="e226" source="n298" target="n299">
      </edge>
    <edge id="e227" source="n298" target="n201">
      </edge>
    <edge id="e228" source="n301" target="n303">
      </edge>
    <edge id="e229" source="n303" target="n302">
      </edge>
    <edge id="e230" source="n89" target="n301">
      </edge>
    <edge id="e231" source="n298" target="n199">
      </edge>
    <edge id="e232" source="n96" target="n304">
      </edge>
    <edge id="e233" source="n304" target="n305">
      </edge>
    <edge id="e234" source="n304" target="n306">
      </edge>
    <edge id="e235" source="n306" target="n279">
      </edge>
    <edge id="e236" source="n305" target="n307">
      </edge>
    <edge id="e237" source="n307" target="n97">
      </edge>
    <edge id="e238" source="n298" target="n308">
      </edge>
    <edge id="e239" source="n308" target="n264">
      </edge>
    <edge id="e240" source="n89" target="n309">
      </edge>
    <edge id="e241" source="n309" target="n310">
      </edge>
    <edge id="e242" source="n309" target="n311">
      </edge>
    <edge id="e243" source="n309" target="n312">
      </edge>
    <edge id="e244" source="n309" target="n265">
      </edge>
    <edge id="e245" source="n309" target="n96">
      </edge>
    <edge id="e246" source="n313" target="n279">
      </edge>
    <edge id="e247" source="n312" target="n255">
      </edge>
    <edge id="e248" source="n310" target="n314">
      </edge>
    <edge id="e249" source="n310" target="n315">
      </edge>
    <edge id="e250" source="n310" target="n316">
      </edge>
    <edge id="e251" source="n310" target="n317">
      </edge>
    <edge id="e252" source="n317" target="n304">
      </edge>
    <edge id="e253" source="n319" target="n318">
      </edge>
    <edge id="e254" source="n314" target="n319">
      </edge>
    <edge id="e255" source="n315" target="n319">
      </edge>
    <edge id="e256" source="n316" target="n320">
      </edge>
    <edge id="e257" source="n311" target="n316">
      </edge>
    <edge id="e258" source="n311" target="n314">
      </edge>
    <edge id="e259" source="n311" target="n315">
      </edge>
    <edge id="e260" source="n311" target="n317">
      </edge>
    <edge id="e261" source="n312" target="n316">
      </edge>
    <edge id="e262" source="n312" target="n314">
      </edge>
    <edge id="e263" source="n312" target="n317">
      </edge>
    <edge id="e264" source="n304" target="n313">
      </edge>
    <edge id="e265" source="n160" target="n321">
      </edge>
    <edge id="e266" source="n321" target="n161">
      </edge>
    <edge id="e267" source="n265" target="n266">
      </edge>
    <edge id="e268" source="n322" target="n323">
      </edge>
    <edge id="e269" source="n0" target="n322">
      </edge>
    <edge id="e270" source="n4" target="n5">
      </edge>
    <edge id="e271" source="n4" target="n7">
      </edge>
    <edge id="e272" source="n4" target="n9">
      </edge>
    <edge id="e273" source="n11" target="n16">
      </edge>
    <edge id="e274" source="n11" target="n14">
      </edge>
    <edge id="e275" source="n11" target="n12">
      </edge>
    <edge id="e276" source="n17" target="n18">
      </edge>
    <edge id="e277" source="n17" target="n20">
      </edge>
    <edge id="e278" source="n17" target="n22">
      </edge>
    <edge id="e279" source="n25" target="n38">
      </edge>
    <edge id="e280" source="n25" target="n32">
      </edge>
    <edge id="e281" source="n25" target="n26">
      </edge>
    <edge id="e282" source="n25" target="n40">
      </edge>
    <edge id="e283" source="n25" target="n30">
      </edge>
    <edge id="e284" source="n25" target="n34">
      </edge>
    <edge id="e285" source="n25" target="n42">
      </edge>
    <edge id="e286" source="n25" target="n36">
      </edge>
    <edge id="e287" source="n25" target="n28">
      </edge>
    <edge id="e288" source="n46" target="n68">
      </edge>
    <edge id="e289" source="n46" target="n47">
      </edge>
    <edge id="e290" source="n46" target="n66">
      </edge>
    <edge id="e291" source="n46" target="n64">
      </edge>
    <edge id="e292" source="n46" target="n58">
      </edge>
    <edge id="e293" source="n46" target="n54">
      </edge>
    <edge id="e294" source="n46" target="n60">
      </edge>
    <edge id="e295" source="n46" target="n62">
      </edge>
    <edge id="e296" source="n46" target="n52">
      </edge>
    <edge id="e297" source="n46" target="n56">
      </edge>
    <edge id="e298" source="n46" target="n50">
      </edge>
    <edge id="e299" source="n74" target="n75">
      </edge>
    <edge id="e300" source="n74" target="n196">
      </edge>
    <edge id="e301" source="n74" target="n77">
      </edge>
    <edge id="e302" source="n100" target="n245">
      </edge>
    <edge id="e303" source="n100" target="n241">
      </edge>
    <edge id="e304" source="n100" target="n101">
      </edge>
    <edge id="e305" source="n100" target="n244">
      </edge>
    <edge id="e306" source="n100" target="n246">
      </edge>
    <edge id="e307" source="n100" target="n242">
      </edge>
    <edge id="e308" source="n100" target="n243">
      </edge>
    <edge id="e309" source="n100" target="n257">
      </edge>
    <edge id="e310" source="n100" target="n116">
      </edge>
    <edge id="e311" source="n100" target="n125">
      </edge>
    <edge id="e312" source="n100" target="n138">
      </edge>
    <edge id="e313" source="n144" target="n245">
      </edge>
    <edge id="e314" source="n144" target="n241">
      </edge>
    <edge id="e315" source="n144" target="n101">
      </edge>
    <edge id="e316" source="n144" target="n244">
      </edge>
    <edge id="e317" source="n144" target="n246">
      </edge>
    <edge id="e318" source="n144" target="n242">
      </edge>
    <edge id="e319" source="n144" target="n243">
      </edge>
    <edge id="e320" source="n144" target="n257">
      </edge>
    <edge id="e321" source="n144" target="n116">
      </edge>
    <edge id="e322" source="n144" target="n125">
      </edge>
    <edge id="e323" source="n144" target="n138">
      </edge>
    <edge id="e324" source="n145" target="n245">
      </edge>
    <edge id="e325" source="n145" target="n241">
      </edge>
    <edge id="e326" source="n145" target="n101">
      </edge>
    <edge id="e327" source="n145" target="n244">
      </edge>
    <edge id="e328" source="n145" target="n246">
      </edge>
    <edge id="e329" source="n145" target="n242">
      </edge>
    <edge id="e330" source="n145" target="n243">
      </edge>
    <edge id="e331" source="n145" target="n257">
      </edge>
    <edge id="e332" source="n145" target="n116">
      </edge>
    <edge id="e333" source="n145" target="n125">
      </edge>
    <edge id="e334" source="n145" target="n138">
      </edge>
    <edge id="e335" source="n143" target="n245">
      </edge>
    <edge id="e336" source="n143" target="n241">
      </edge>
    <edge id="e337" source="n143" target="n101">
      </edge>
    <edge id="e338" source="n143" target="n244">
      </edge>
    <edge id="e339" source="n143" target="n246">
      </edge>
    <edge id="e340" source="n143" target="n242">
      </edge>
    <edge id="e341" source="n143" target="n243">
      </edge>
    <edge id="e342" source="n143" target="n257">
      </edge>
    <edge id="e343" source="n143" target="n116">
      </edge>
    <edge id="e344" source="n143" target="n125">
      </edge>
    <edge id="e345" source="n143" target="n138">
      </edge>
    <edge id="e346" source="n243" target="n104">
      </edge>
    <edge id="e347" source="n243" target="n102">
      </edge>
    <edge id="e348" source="n243" target="n106">
      </edge>
    <edge id="e349" source="n243" target="n112">
      </edge>
    <edge id="e350" source="n243" target="n114">
      </edge>
    <edge id="e351" source="n243" target="n259">
      </edge>
    <edge id="e352" source="n243" target="n108">
      </edge>
    <edge id="e353" source="n243" target="n110">
      </edge>
    <edge id="e354" source="n242" target="n104">
      </edge>
    <edge id="e355" source="n242" target="n102">
      </edge>
    <edge id="e356" source="n242" target="n106">
      </edge>
    <edge id="e357" source="n242" target="n112">
      </edge>
    <edge id="e358" source="n242" target="n114">
      </edge>
    <edge id="e359" source="n242" target="n259">
      </edge>
    <edge id="e360" source="n242" target="n108">
      </edge>
    <edge id="e361" source="n242" target="n110">
      </edge>
    <edge id="e362" source="n246" target="n104">
      </edge>
    <edge id="e363" source="n246" target="n102">
      </edge>
    <edge id="e364" source="n246" target="n106">
      </edge>
    <edge id="e365" source="n246" target="n112">
      </edge>
    <edge id="e366" source="n246" target="n114">
      </edge>
    <edge id="e367" source="n246" target="n259">
      </edge>
    <edge id="e368" source="n246" target="n108">
      </edge>
    <edge id="e369" source="n246" target="n110">
      </edge>
    <edge id="e370" source="n244" target="n104">
      </edge>
    <edge id="e371" source="n244" target="n102">
      </edge>
    <edge id="e372" source="n244" target="n106">
      </edge>
    <edge id="e373" source="n244" target="n112">
      </edge>
    <edge id="e374" source="n244" target="n114">
      </edge>
    <edge id="e375" source="n244" target="n259">
      </edge>
    <edge id="e376" source="n244" target="n108">
      </edge>
    <edge id="e377" source="n244" target="n110">
      </edge>
    <edge id="e378" source="n101" target="n104">
      </edge>
    <edge id="e379" source="n101" target="n102">
      </edge>
    <edge id="e380" source="n101" target="n106">
      </edge>
    <edge id="e381" source="n101" target="n112">
      </edge>
    <edge id="e382" source="n101" target="n114">
      </edge>
    <edge id="e383" source="n101" target="n259">
      </edge>
    <edge id="e384" source="n101" target="n108">
      </edge>
    <edge id="e385" source="n101" target="n110">
      </edge>
    <edge id="e386" source="n241" target="n104">
      </edge>
    <edge id="e387" source="n241" target="n102">
      </edge>
    <edge id="e388" source="n241" target="n106">
      </edge>
    <edge id="e389" source="n241" target="n112">
      </edge>
    <edge id="e390" source="n241" target="n114">
      </edge>
    <edge id="e391" source="n241" target="n259">
      </edge>
    <edge id="e392" source="n241" target="n108">
      </edge>
    <edge id="e393" source="n241" target="n110">
      </edge>
    <edge id="e394" source="n245" target="n104">
      </edge>
    <edge id="e395" source="n245" target="n102">
      </edge>
    <edge id="e396" source="n245" target="n106">
      </edge>
    <edge id="e397" source="n245" target="n112">
      </edge>
    <edge id="e398" source="n245" target="n114">
      </edge>
    <edge id="e399" source="n245" target="n259">
      </edge>
    <edge id="e400" source="n245" target="n108">
      </edge>
    <edge id="e401" source="n245" target="n110">
      </edge>
    <edge id="e402" source="n248" target="n104">
      </edge>
    <edge id="e403" source="n248" target="n102">
      </edge>
    <edge id="e404" source="n248" target="n106">
      </edge>
    <edge id="e405" source="n248" target="n112">
      </edge>
    <edge id="e406" source="n248" target="n114">
      </edge>
    <edge id="e407" source="n248" target="n259">
      </edge>
    <edge id="e408" source="n248" target="n108">
      </edge>
    <edge id="e409" source="n248" target="n110">
      </edge>
    <edge id="e410" source="n247" target="n104">
      </edge>
    <edge id="e411" source="n247" target="n102">
      </edge>
    <edge id="e412" source="n247" target="n106">
      </edge>
    <edge id="e413" source="n247" target="n112">
      </edge>
    <edge id="e414" source="n247" target="n114">
      </edge>
    <edge id="e415" source="n247" target="n259">
      </edge>
    <edge id="e416" source="n247" target="n108">
      </edge>
    <edge id="e417" source="n247" target="n110">
      </edge>
    <edge id="e418" source="n116" target="n123">
      </edge>
    <edge id="e419" source="n116" target="n121">
      </edge>
    <edge id="e420" source="n116" target="n119">
      </edge>
    <edge id="e421" source="n116" target="n117">
      </edge>
    <edge id="e422" source="n125" target="n136">
      </edge>
    <edge id="e423" source="n125" target="n126">
      </edge>
    <edge id="e424" source="n125" target="n128">
      </edge>
    <edge id="e425" source="n125" target="n132">
      </edge>
    <edge id="e426" source="n125" target="n134">
      </edge>
    <edge id="e427" source="n125" target="n130">
      </edge>
    <edge id="e428" source="n138" target="n139">
      </edge>
    <edge id="e429" source="n138" target="n141">
      </edge>
    <edge id="e430" source="n151" target="n99">
      </edge>
    <edge id="e431" source="n324" target="n99">
      </edge>
    <edge id="e432" source="n167" target="n99">
      </edge>
    <edge id="e433" source="n163" target="n99">
      </edge>
    <edge id="e434" source="n171" target="n99">
      </edge>
    <edge id="e435" source="n261" target="n99">
      </edge>
    <edge id="e436" source="n190" target="n99">
      </edge>
    <edge id="e437" source="n187" target="n99">
      </edge>
    <edge id="e438" source="n325" target="n214">
      </edge>
    <edge id="e439" source="n326" target="n327">
      </edge>
    <edge id="e440" source="n298" target="n326">
      </edge>
    <edge id="e441" source="n153" target="n329">
      </edge>
    <edge id="e442" source="n329" target="n154">
      </edge>
    <edge id="e443" source="n155" target="n328">
      </edge>
    <edge id="e444" source="n328" target="n156">
      </edge>
    <edge id="e445" source="n92" target="n331">
      </edge>
    <edge id="e446" source="n331" target="n93">
      </edge>
    <edge id="e447" source="n92" target="n330">
      </edge>
    <edge id="e448" source="n330" target="n333">
      </edge>
    <edge id="e449" source="n333" target="n332">
      </edge>
    <edge id="e450" source="n79" target="n334">
      </edge>
    <edge id="e451" source="n79" target="n335">
      </edge>
    <edge id="e452" source="n334" target="n336">
      </edge>
    <edge id="e453" source="n334" target="n337">
      </edge>
    <edge id="e454" source="n334" target="n338">
      </edge>
    <edge id="e455" source="n335" target="n339">
      </edge>
    <edge id="e456" source="n336" target="n80">
      </edge>
    <edge id="e457" source="n337" target="n340">
      </edge>
    <edge id="e458" source="n338" target="n341">
      </edge>
    <edge id="e459" source="n339" target="n342">
      </edge>
    <edge id="e460" source="n94" target="n343">
      </edge>
    <edge id="e461" source="n94" target="n344">
      </edge>
    <edge id="e462" source="n344" target="n95">
      </edge>
    <edge id="e463" source="n343" target="n345">
      </edge>
    <edge id="e464" source="n343" target="n346">
      </edge>
    <edge id="e465" source="n343" target="n347">
      </edge>
    <edge id="e466" source="n343" target="n348">
      </edge>
    <edge id="e467" source="n345" target="n95">
      </edge>
    <edge id="e468" source="n346" target="n95">
      </edge>
    <edge id="e469" source="n347" target="n95">
      </edge>
    <edge id="e470" source="n348" target="n95">
      </edge>
    <edge id="e471" source="n0" target="n349">
      </edge>
    <edge id="e472" source="n349" target="n350">
      </edge>
    <edge id="e473" source="n89" target="n351">
      </edge>
    <edge id="e474" source="n351" target="n353">
      </edge>
    <edge id="e475" source="n351" target="n352">
      </edge>
    <edge id="e476" source="n352" target="n354">
      </edge>
    <edge id="e477" source="n353" target="n354">
      </edge>
    <edge id="e478" source="n355" target="n293">
      </edge>
    <edge id="e479" source="n293" target="n180">
      </edge>
    <edge id="e480" source="n356" target="n180">
      </edge>
    <edge id="e481" source="n179" target="n355">
      </edge>
    <edge id="e482" source="n179" target="n357">
      </edge>
    <edge id="e483" source="n357" target="n356">
      </edge>
  </graph>
  <data key="d14">
    <y:Resources/>
  </data>
</graphml>
